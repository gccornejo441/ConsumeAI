import requests

def request_page(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
    except requests.RequestException:
        return None

def get_page_urls():
    for i in range(1,2):
        baseurl = 'https://www.facebook.com/{}'.format(i)
        html = request_page(baseurl)
        


if __name__ == "__main__":
    url = "https://google.com"
    page_content = request_page(url)
    print(page_content)


