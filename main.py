import streamlit as st
import os
import yt_dlp
import pandas as pd
import requests
import re
import subprocess
import time
from rembg import remove
from PIL import Image
from urllib.parse import urlparse, parse_qs

st.set_page_config(layout='centered')

def clear_text():
    st.session_state["url"] = ""
    

input_path = 'YT-DLP.png'
output_path = 'YT-DLP-rembg.png'
input = Image.open(input_path)
output = remove(input)
output.save(output_path)


def get_video_id(url):
    parsed = urlparse(url)
    if parsed.hostname == 'www.youtube.com' or parsed.hostname == 'youtube.com':
        if 'v' in parse_qs(parsed.query):
            return parse_qs(parsed.query)['v'][0]
    return None


image = Image.open('YT-DLP-rembg.png', "r")
st.image(image,width=200, use_column_width="auto")
st.header("YT-DLP X Streamlit", )
url = st.text_input("Enter Youtube Vedio URL:", key="url")
video_id = get_video_id(url)
thumbnail_url = f"https://img.youtube.com/vi/{video_id}/0.jpg"



if url:
    with yt_dlp.YoutubeDL() as yydl:
        info_dict = yydl.extract_info(url, download=False)
        video_tile = info_dict.get('title', None)
    video_length = subprocess.getoutput(f'yt-dlp {url} --print duration_string')
    st.subheader(f'{video_tile}\nLength: {video_length} seconds', divider='green') 


    
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
        df_12 = df.iloc[:, :12]

        def swap_columns(df, col1, col2):
            col_list = list(df_12.columns)
            x, y = col_list.index(col1), col_list.index(col2)
            col_list[y], col_list[x] = col_list[x], col_list[y]
            df = df_12[col_list]
            return df
        df = swap_columns(df, 'protocol', 'resolution')

    new_df = df.iloc[:, :9]
    indexs = new_df.index[:]
    store_index = []
    user_input_container = st.empty()
    for i in indexs:
        store_index.append(i)
    format_id = new_df['format_id'] #ID
    
    with st.expander('Vedio thumbnail image'):
        st.image(thumbnail_url, use_column_width=True)

    df2 = [s for sublist in format_id.apply(str).str.split() for s in sublist if s] #Show format_id
    with user_input_container.container():
        format_id_type = st.selectbox("Select format ID to Download", options=df2, key='ID')
 
    my_download = st.button(f'Download format ID:{format_id_type}')

    with st.expander(f'Show available streams ({len(store_index)})'):
        st.dataframe(new_df.iloc[::-1].reset_index(drop=True))

    src_dir = "D:\Youtube vedio project"
    if my_download:
        get_video = subprocess.getoutput(f'yt-dlp -f {format_id_type} {url}')
        cmd = f'yt-dlp -f {format_id_type} {url} --print filename --encoding utf-8'
        filename = subprocess.run(cmd, capture_output=True,shell=True, text=True, encoding='utf-8').stdout        
        # if os.path.exists(my_file):
        link = 'http://file.io/'
        with open(filename.strip('\n'), 'rb') as f:
            requests_link = requests.post(link, files={'file':f})
            res = requests_link.json()
            the_link = res["link"]
            st.markdown(f"[Download Link]({the_link})")
            st.success('Download completed')
            time.sleep(3)
        os.remove(filename.strip('\n'))
else:
    st.warning("Please enter a valid Youtube Vedio URL ")
        
st.button("Clear all address boxes", on_click=clear_text)

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
    '<style>.st-cd{padding-bottom:10px}',unsafe_allow_html=True

)

st.markdown(
    '<style>.st-cc{padding-top:10px}',unsafe_allow_html=True

)

st.markdown(
    '<style>.st-cg{line-height:1.6}',unsafe_allow_html=True

)
    
st.markdown(
    '<style>h3{font-size:1.25rem}',unsafe_allow_html=True
)









