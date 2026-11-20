"""Replace the labels on the movie gallery frame and its five tabs."""

FOOTER = {
    'P': ('11110','10001','10001','11110','10000','10000','10000'),
    'E': ('11111','10000','10000','11110','10000','10000','11111'),
    'L': ('10000','10000','10000','10000','10000','10000','11111'),
    'Í': ('00110','00000','01110','00100','00100','00100','01110'),
    'C': ('01111','10000','10000','10000','10000','10000','01111'),
    'U': ('10001','10001','10001','10001','10001','10001','01110'),
    'A': ('01110','10001','10001','11111','10001','10001','10001'),
    'S': ('01111','10000','10000','01110','00001','00001','11110'),
}

def movie_frame(raw):
    data = bytearray(raw)
    # Base tray and its five selected-tab variants share the same ordinal art.
    tab_backgrounds = (18,23,28,34,39)
    tab_ink = (21,26,31,37,42)
    for i, (background, ink) in enumerate(zip(tab_backgrounds, tab_ink)):
        for offset, width, x in ((0,240,17+40*i),(0xbd00+0x300*i,48,17)):
            for y in range(6,13):
                at = offset+y*width+x+7
                row = data[at:at+10]
                if len(row) != 10 or not set(row) <= {background, ink, background+1, background-1}:
                    raise ValueError("OMALL: colores de pestaña no reconocidos")
                data[at:at+10] = bytes([background])*len(row)
            for dx,dy in ((7,11),(9,6),(10,6),(8,7),(11,7),(9,8),(10,8)):
                at = offset+dy*width+x+dx
                if data[at] != background:
                    raise ValueError("OMALL: fondo de pestaña no reconocido")
                data[at] = ink

    at, width = 0xb4c0, 88
    label = 'PELÍCULAS'
    width_text = len(label)*6-1
    x = (width-width_text)//2
    for y in range(8,17):
        for col in range(7,80):
            index = at+y*width+col
            if data[index] in {1,2,3,5}:
                data[index] = 2
    coords = [(x+i*6+dx, 8+dy) for i,char in enumerate(label)
              for dy,row in enumerate(FOOTER[char]) for dx,ink in enumerate(row) if ink=='1']
    for col,y in coords:
        data[at+(y+1)*width+col+1] = 5
    for col,y in coords:
        data[at+y*width+col] = 1
    return bytes(data)
