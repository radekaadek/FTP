import os

def load_points():
    import pandas as pd
    import numpy as np
    import os

    # load xls
    dfs = []
    for file in os.listdir(directory):
        if file.endswith('.xlsx'):
            df = pd.read_excel(f"{directory}/{file}")
            dfs.append(df)

    print(dfs[0])

    # save csv to test.csv
    dfs[0].to_csv('test.csv')

    print(dfs[0])

    # unnamed 9, 7 is x
    # unnamed 12, 7 is y
    # unnamed 15, 7 is z
    xyzs = []
    for d in dfs:
        xyzs.append(np.array([d['Unnamed: 18'][5], d['Unnamed: 9'][5], d['Unnamed: 12'][5], d['Unnamed: 15'][5]]))
    xyzsnp = np.array(xyzs)
    print(xyzsnp)

    # save to csv
    with open('xyz.csv', 'w') as f:
        for i in range(len(xyzsnp)):
            f.write(f"{xyzsnp[i][0]},{xyzsnp[i][1]},{xyzsnp[i][2]},{xyzsnp[i][3]}\n")

    return xyzsnp

app.addMenuItem("mojprzycisk", load_points)
