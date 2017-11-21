# first line: 163
@memory.cache
def feat_time_elapsed(link):
    long_text = read_file(link, 'Speeches', 'html')
    try:
        url = list(set(re.findall(r'https:\/\/.*\.mp3', long_text)))[0]
    except: #There is no audio URL
        return 10000. #Now the words/second is going to be tiny. But better than it being huge soooo......

    r = requests.get(url, stream=True)

    length_audiofile = r.headers['Content-length']
    seconds = int(length_audiofile) / 6000
    return seconds
