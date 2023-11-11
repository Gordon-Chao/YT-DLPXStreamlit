import streamlit as st
import os
import yt_dlp
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import pandas as pd
import requests
import re
import subprocess
import time
from PIL import Image
from urllib.parse import urlparse, parse_qs

st.set_page_config(layout='centered')

def clear_text():
    st.session_state["url"] = ""
    st.session_state['box'] = False
    st.session_state['bpg'] = False
    return

def get_video_id(url):
    parsed = urlparse(url)
    if parsed.hostname == 'www.youtube.com' or parsed.hostname == 'youtube.com':
        if 'v' in parse_qs(parsed.query):
            return parse_qs(parsed.query)['v'][0]
    return None


image = Image.open('myLinzy.png', "r")
st.image(image, use_column_width="auto")
st.header("YT-DLP X Streamlit", )
url = st.text_input("Enter Youtube Vedio URL:", key="url")
bprogressive = st.checkbox('Progressive streams', value=False, key='bpg', help=f'[What is progressive streams ?](https://pytube.io/en/latest/user/streams.html)')
checkbox = st.checkbox('audio only', value=False, key='box')
video_id = get_video_id(url)
thumbnail_url = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"



if url:
    with yt_dlp.YoutubeDL() as yydl:
        info_dict = yydl.extract_info(url, download=False)
        video_tile = info_dict.get('title', None)
    video_length = subprocess.getoutput(f'yt-dlp {url} --print duration_string')
    st.subheader(f'{video_tile}\nLength: :green[{video_length}] seconds', divider='green') 
    with st.expander('Vedio thumbnail image'):
        st.image(thumbnail_url, use_column_width=True)

    
def is_valid_url(url):
    youtube_url_pattern = re.compile(r'^https?://(www\.)?youtube\.com/watch\?v=[\w-]+')
    return bool(youtube_url_pattern.match(url))
if is_valid_url(url):
    ydl_opts = {
    'listformats': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False) 
        data = pd.DataFrame()
        df = pd.DataFrame(ydl.sanitize_info(info_dict).get("formats"))
        df.pop('http_headers')
        df.pop('manifest_url')
        df.pop('fragments')
        df.pop('dynamic_range')
        df.pop('downloader_options')
        df.pop('filesize_approx')
        df.pop('url')
        # df_12 = df.iloc[:, :12]

        def swap_columns(df, col1, col2, col3, col4):
            col_list = list(df.columns)
            x, y = col_list.index(col1), col_list.index(col2)
            x1, y1 = col_list.index(col3), col_list.index(col4)
            col_list[y], col_list[x] = col_list[x], col_list[y]
            col_list[y1], col_list[x1] = col_list[x1], col_list[y1]
            df = df[col_list]
            return df
        df = swap_columns(df, 'protocol', 'resolution', 'tbr', 'filesize')

    new_df = df.iloc[:, :9].drop(columns=['width', 'height'])
    def add_k(value):
        if pd.notna(value) and value != 0:
            return f'{int(value)}KBit/s'
        else:
            return value
    df['vbr'] = df['vbr'].round(0).apply(add_k).replace(0.0, 'none')
    df['abr'] = df['abr'].round(0).apply(add_k).replace(0.0, 'none')
    df['fps'] = df['fps'].apply(lambda x: f'{x:g}')
    loc_df = df.loc[:, 'vbr':]

    

    
    for index, size in enumerate(loc_df['filesize']):
        if pd.notna(size):
            if size < 1024 * 1024:
                loc_df.at[index, 'filesize'] = f'{round(size / 1024, 2):g}KB'
            else:
                loc_df.at[index, 'filesize'] = f'{round(size / (1024**2), 2):g}MB'
        
    concat_df = pd.concat([new_df, loc_df], axis=1).iloc[:, :10]
    mod_df = concat_df.drop(concat_df[concat_df['format_note'] == 'storyboard'].index)
    
    store_index = []
    
    if checkbox:
        new = mod_df.loc[mod_df['resolution'] == 'audio only']
        mod_df = new
        format_id = mod_df['format_id']
        indexs = mod_df.index[:]
        for i in indexs:
            store_index.append(i)
    elif bprogressive:
        new = concat_df[(concat_df['acodec'] != 'none') & (concat_df['vcodec'] != 'none')]
        mod_df = new
        format_id = mod_df['format_id']
        indexs = mod_df.index[:]
        for i in indexs:
            store_index.append(i)
    else:
        format_id = mod_df['format_id'] #ID
        indexs = mod_df.index[:]
        for i in indexs:
            store_index.append(i)
    
    
    df2 = [s for sublist in format_id.apply(str).str.split() for s in sublist if s] #Show format_id
    
    format_id_type = st.selectbox("Select format ID to Download", options=df2, key='ID')
    
    my_download = st.button(f'Download format ID: {format_id_type}')
    

    a = len(store_index)
    if checkbox and bprogressive:
        b = 'Not found'
        a = b

    with st.expander(f'Show available streams ({a})'):
        if checkbox and bprogressive:
            st.write('No results')
        else:
            st.dataframe(mod_df.iloc[::-1].reset_index(drop=True).style.format({'fps': '{:g}'}))
    try:    
        if my_download:
            get_video = subprocess.getoutput(f'yt-dlp -f {format_id_type} {url}')
            cmd = f'yt-dlp -f {format_id_type} {url} --print filename --encoding utf-8'
            filename = subprocess.run(cmd, capture_output=True,shell=True, text=True, encoding='utf-8').stdout        
            link = 'http://file.io/'
            with open(filename.strip('\n'), 'rb') as f:
                requests_link = requests.post(link, files={'file':f})
                res = requests_link.json()
                the_link = res["link"]
                st.markdown(f"[Download Link]({the_link})")
                st.success('Download completed')
                time.sleep(3)
            os.remove(filename.strip('\n'))
    except Exception as e:
        st.warning(f'Download Error:{e}')

else:
    st.warning("Please enter a valid Youtube Vedio URL ")
          
st.button("Clear all address boxes", on_click=clear_text)


st.markdown(
    '<style>.s1jz82f8 .dvn-scroller{background:linear-gradient(0deg, rgba(147,34,195,0.6705334233302696) 22%, rgba(45,253,246,0.7433625549829307) 84%);opacity:0.5}</style>',unsafe_allow_html=True
)



st.markdown(
    '<style>.st-emotion-cache-10oheav h1{position:relative;top:-50px;}</style>', unsafe_allow_html=True
    
    )

st.markdown(
    '<style>h2{font-family:"IBM Plex Sans", sans-serif;font-weight:400;line-height:1;font-size: calc(1.3rem + .6vw)}',unsafe_allow_html=True
)

st.markdown(
    '<style>.st-emotion-cache-eczf16{top: calc(-1.25rem + 0.5em);left:0px;}</style>', unsafe_allow_html=True
)


st.markdown(
    '<style>.st-cf{padding-right:14px}',unsafe_allow_html=True
)

st.markdown(
    '<style>.st-ce{padding-left:14px}',unsafe_allow_html=True
)

st.markdown(
    '<style>.st-cd{padding-bottom:7px}',unsafe_allow_html=True

)

st.markdown(
    '<style>.st-cc{padding-top:7px}',unsafe_allow_html=True

)

st.markdown(
    '<style>.st-cg{line-height:1.4}',unsafe_allow_html=True

)
    
st.markdown(
    '<style>h3{font-size:1.25rem}',unsafe_allow_html=True
)









