import requests

endpoint = "https://chart.apis.google.com/chart?"


class Chart:

    cht = "lc"
    chs = "300x200"
    chtt = "Some stats"
    chxt = "x,y"
    chxl = "0:/Yesterday/Today"
    chd = "t:69,30,10"

def draw_n_save(chart, filename):
    global endpoint
    url = endpoint
    arr = {
        'cht': chart.cht,
        'chs': chart.chs,
        'chtt': chart.chtt,
        'chxt': chart.chxt,
        'chxl': chart.chxl,
        'chd': chart.chd
    }
    url += "&".join([f"{item[0]}={item[1]}" for item in arr.items()])
    r = requests.get(url)
    with open(filename, 'wb') as f:
        f.write(r.content)

if __name__ == "__main__":
    chart = Chart()
    draw_n_save(chart, "chart.png")