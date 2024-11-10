import json
import pandas as pd


def main():
    with open('../data_line/pine_sorrel/wpd.json', 'r') as f:
        data = json.load(f)

    data1 = data['datasetColl']
    data2 = data1[0]
    data3 = data2['data']

    b = []
    for i in range(len(data3)):
        a = data3[i]
        b.append(a["value"])

    df = pd.DataFrame(b, columns=['x', 'y'])
    print(df.head())

    df.to_json('../data_line/tmp_data.json', orient='records')


if __name__ == '__main__':
    main()
