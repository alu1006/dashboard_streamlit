from datetime import datetime, timedelta
import time
import folium
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import math
from streamlit_autorefresh import st_autorefresh  # Properly import st_autorefresh
import requests

import ssl
ssl._create_default_https_context = ssl._create_unverified_context


# 必須是第一個 Streamlit 指令
st.set_page_config(layout='wide',page_title='桃園市相關數據展示' ,initial_sidebar_state='expanded')

# Streamlit 文字指令
st.title('桃園市相關數據展示')
st.write('### 中壢高商乙丙級通過率')
# st.sidebar.header('Dashboard `version 2`')



#104 73
# 84    48
# 7651	3654
# 6874	3370
col1, col2,col3, col4 = st.columns(4)
col1.metric('112年度電乙本校參檢人數', 84, delta=-20, delta_color="inverse", help=None)
col2.metric('112年度電乙全國參檢人數', 6874, delta=7651-6874, delta_color="inverse", help=None)
col3.metric('112年度電乙本校通過率', f'{48/84*100:.2f}%', delta='-13.1%', delta_color="inverse", help=None)
col4.metric('112年度電乙全國通過率', f'{3370/6874*100:.2f}%', delta=f'{((3370/6874)-(3654/7651))*100:.2f}%', delta_color="inverse", help=None)

# --------------------------------

data = {
    '年': [1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022],
    '臺灣地區-元': [1070268, 1089575, 1091478, 1064136, 1064153, 1064825, 1074665, 1082168, 1099739, 1108674, 1099994, 1074180, 1071938, 1104265, 1122379, 1140271, 1157926, 1167284, 1194572, 1231112, 1249031, 1274196, 1293719, 1314023, 1340848],
    '新北市-元': [1087242, 1102563, 1095192, 1098408, 1100003, 1093053, 1109639, 1135398, 1125605, 1099472, 1159279, 1110774, 1071131, 1116342, 1101389, 1129598, 1146991, 1171978, 1223867, 1265798, 1292753, 1319841, 1352548, 1381603, 1421385],
    '臺北市-元': [1442675, 1472979, 1530735, 1505506, 1514440, 1501916, 1488180, 1514069, 1526228, 1550134, 1538257, 1515793, 1564298, 1537890, 1570778, 1545415, 1575819, 1581899, 1568945, 1648122, 1649348, 1723021, 1716591, 1732126, 1752411],
    '桃園市-元': [1163181, 1174654, 1209363, 1143050, 1192731, 1163092, 1203215, 1192419, 1179444, 1210511, 1182721, 1146080, 1122238, 1183732, 1238698, 1257146, 1327963, 1307158, 1317790, 1337361, 1378732, 1392199, 1424027, 1448909, 1449549],
    '臺中市-元': [1102701, 1137007, 1038480, 1055944, 1015972, 1023452, 990633, 988496, 1048174, 1105239, 1026631, 977731, 987259, 1100346, 1067060, 1126875, 1152523, 1169183, 1140325, 1245350, 1279865, 1298497, 1289700, 1304508, 1338826],
    '臺南市-元': [911488, 896601, 933736, 872189, 898270, 936057, 943051, 881412, 950332, 972699, 976116, 924950, 886924, 948383, 927231, 996434, 991990, 1007093, 1063495, 1079199, 1086077, 1079174, 1086475, 1120580, 1143699],
    '高雄市-元': [1029317, 1051762, 1031569, 1003108, 974592, 972280, 1011408, 1046729, 1030212, 1081799, 1068765, 1052162, 1052260, 1043941, 1085971, 1107383, 1112287, 1145895, 1166824, 1186204, 1219246, 1224668, 1224100, 1231562, 1263068],
    '宜蘭縣-元': [976550, 1022506, 972996, 877199, 846963, 943028, 874576, 994967, 931588, 909097, 1006018, 904809, 971775, 877016, 1075706, 979013, 1071335, 1160320, 1085846, 1098807, 1069997, 1093475, 1138365, 1136419, 1165558],
    '新竹縣-元': [1113042, 1167454, 1232173, 1106603, 1127123, 1133617, 1196515, 1304360, 1164274, 1098234, 1289463, 1281933, 1300116, 1372358, 1367712, 1346768, 1389453, 1283995, 1365150, 1616327, 1519478, 1539555, 1619782, 1689337, 1702134],
    '苗栗縣-元': [943047, 945975, 935836, 944066, 921405, 949888, 895950, 931906, 1030851, 1000447, 919930, 926267, 964594, 1014144, 1012306, 1020185, 1100084, 1008241, 1166196, 1029485, 1045881, 1073028, 1161999, 1214424, 1273250],
    '彰化縣-元': [951047, 891310, 897000, 845708, 943182, 962720, 945506, 906328, 961572, 922001, 902838, 890929, 887707, 920937, 953701, 936595, 940572, 926717, 994353, 970491, 997162, 1026792, 996066, 1086809, 1108221],
    '南投縣-元': [875980, 1005079, 874344, 836262, 830936, 819394, 879780, 897891, 964953, 860836, 851992, 978331, 932725, 881743, 986881, 896557, 919551, 878760, 916199, 894368, 967369, 940893, 997605, 985686, 1048879],
    '雲林縣-元': [782106, 889682, 810634, 873803, 817942, 809617, 849594, 769997, 906358, 794205, 767431, 744181, 748256, 817778, 824211, 838094, 865131, 876670, 896101, 868663, 860237, 933883, 988062, 1024191, 1016913],
    '嘉義縣-元': [707349, 766905, 857615, 783819, 730084, 738385, 778574, 797895, 810323, 750236, 764933, 741766, 775017, 804668, 880625, 858253, 789406, 890742, 896217, 901022, 940780, 850597, 906554, 916631, 891498],
    '屏東縣-元': [919710, 879362, 913848, 838027, 927042, 919906, 847872, 894772, 899657, 953471, 842372, 877498, 850116, 866795, 889560, 861063, 832681, 869818, 911258, 958999, 985681, 964547, 1064508, 1046302, 1083933],
    '臺東縣-元': [702299, 725065, 780967, 760989, 774329, 737947, 755711, 695369, 753191, 860701, 699334, 805395, 674899, 733168, 796622, 799026, 820549, 746981, 797395, 889108, 884510, 874386, 891340, 911136, 916928],
    '花蓮縣-元': [887914, 883537, 933625, 933484, 845923, 880361, 858345, 795376, 862688, 878356, 843646, 808632, 904472, 920602, 927400, 966607, 860613, 924706, 948501, 910090, 937898, 956973, 1032499, 1026488, 1010041],
    '澎湖縣-元': [634053, 723916, 831230, 732306, 760406, 739670, 874714, 778659, 853872, 789752, 902952, 851835, 986954, 828441, 887077, 922916, 932694, 792696, 1069545, 857821, 959761, 1037554, 1091011, 796484, 919357],
    '基隆市-元': [999088, 1058154, 1052113, 964170, 893884, 881716, 1048399, 1052699, 948817, 999562, 976639, 1026166, 1040931, 1018118, 955197, 1002341, 957360, 1072433, 1074314, 1096361, 1070748, 1140481, 1106963, 1111556, 1099526],
    '新竹市-元': [1207558, 1268541, 1395702, 1419946, 1320717, 1344434, 1479816, 1361016, 1478303, 1554456, 1462204, 1426854, 1448209, 1479675, 1439066, 1535411, 1576797, 1427572, 1537317, 1572296, 1426379, 1602826, 1618903, 1602415, 1722889],
    '嘉義市-元': [1059622, 958462, 1005451, 975877, 1015957, 927635, 832402, 984171, 966863, 899387, 898229, 836551, 842337, 925444, 1095203, 1241161, 1157962, 1106004, 1154411, 1090947, 1152499, 1208298, 1225219, 1217617, 1282798]
}
df = pd.DataFrame(data)
plt.rc('font', family='Arial Unicode Ms')
col_rowB_1, col_rowB_2 = st.columns((7,3))
with col_rowB_1:
    st.write('### 桃園區與臺灣地區收入變化')
    
    # 在 sidebar 中添加多選選項
    st.sidebar.subheader('收入-選擇地區')
    selected_areas = st.sidebar.multiselect(
        '選擇地區',
        options=df.columns[1:],  # 不包含 '年' 欄位
        default=['臺灣地區-元', '新北市-元', '臺北市-元', '桃園市-元']  # 預設選擇
        
    )

    # 使用 plotly 建立折線圖
    fig = go.Figure()

    # 添加每個選取的地區到圖表中
    for area in selected_areas:
        fig.add_trace(go.Scatter(x=df['年'], y=df[area], mode='lines+markers', name=area))

    # 設定圖表標題和軸標籤
    fig.update_layout(
        #title='各地區收入變化',
        xaxis_title='年份',
        yaxis_title='收入 (元)',
        hovermode='x',
        width=700  # 設定圖表寬度
        
    )


    # 在 Streamlit 中顯示圖表
    st.plotly_chart(fig,use_container_width=True)
with col_rowB_2:
    st.write('### 原始資料')
    st.write(df)
    

#--------------------------------
# Row C
st.write('## 桃園區廟宇登記數量分析')
col_rowC_1, col_rowC_2 = st.columns((5,5))
with col_rowC_1:
    st.write('### 桃園市各廟宇主祀神祇比例')

    # 從 API 讀取 JSON 數據
    data = pd.read_json('http://data.tycg.gov.tw/api/v1/rest/datastore/b2247404-3d92-4829-9855-0cd5e71b92b3?format=json&limit=500')
    df = pd.DataFrame(data['result']['records'])

    # 計算各主祀神祇的數量和比例
    df_count = df['主祀神祇'].value_counts(normalize=True)
    df_count_ratio = df_count / df_count.sum()
    # 計算 "其他" 的比例
    df_count_ratio['其他'] = df_count_ratio[df_count_ratio < 0.03].sum()

    # 保留比例大於等於 3% 的項目，並包含 "其他"
    df_count_ratio = df_count_ratio[df_count_ratio >= 0.03]
    # 在 Streamlit sidebar 中創建多選篩選
    # 轉換為純字串列表
    st.sidebar.subheader('比例-選擇主祀神祇')
    options_list = df_count_ratio.index.astype(str).tolist()
    selected_labels = st.sidebar.multiselect(
        '選擇主祀神祇',
        options=options_list,
        default=options_list  # 預設顯示全部
    )
   

    # 根據選擇篩選數據
    filtered_data = df_count_ratio[selected_labels]

    # 使用 Plotly 繪製互動式圓餅圖
    fig = px.pie(
        values=filtered_data,
        names=filtered_data.index,
        title='',
        hole=0.4 , # 設置為甜甜圈圖表
        width=400  # 設定圖表寬度
    )

    # 更新圖表樣式
    fig.update_traces(textinfo='percent+label')

    # 在 Streamlit 中顯示圖表
    st.plotly_chart(fig)

with col_rowC_2:
    st.write('### 桃園市廟數量與教別分析')
    # 建立交叉表，顯示不同主祀神祇所對應的教別數量
    cross_table = pd.crosstab(df['主祀神祇'], df['教別']).reset_index()

    # 計算每個神祇的總寺廟數量
    cross_table['總寺廟數量'] = cross_table.iloc[:, 1:].sum(axis=1)

    # 在 sidebar 中添加篩選選項：根據總寺廟數量篩選
    min_count, max_count = st.sidebar.slider(
        '選擇寺廟數量篩選範圍',
        min_value=int(cross_table['總寺廟數量'].min()),
        max_value=int(cross_table['總寺廟數量'].max()),
        value=(int(cross_table['總寺廟數量'].min()), int(cross_table['總寺廟數量'].max()))
    )

    # 根據數量範圍篩選神祇
    filtered_table = cross_table[(cross_table['總寺廟數量'] >= min_count) & (cross_table['總寺廟數量'] <= max_count)]

    # 去除 "總寺廟數量" 列，轉換為長格式
    filtered_table_long = filtered_table.drop(columns='總寺廟數量').melt(id_vars='主祀神祇', var_name='教別', value_name='寺廟數量')

    # 去除寺廟數量為 0 的項目
    filtered_table_long = filtered_table_long[filtered_table_long['寺廟數量'] > 0]

    # 使用 Plotly 繪製長條圖
    fig = px.bar(
        filtered_table_long,
        x='主祀神祇',
        y='寺廟數量',
        color='教別',
        barmode='group',
        title='',
        labels={'寺廟數量': '寺廟數量', '主祀神祇': '主祀神祇', '教別': '教別'}
    )

    # 在 Streamlit 中顯示長條圖
    st.plotly_chart(fig)



#--------------------------------
# 設定自動刷新間隔（秒）
refresh_interval = 30  # seconds
st_autorefresh(interval=refresh_interval * 1000)  # interval 以毫秒為單位
# 顯示標題
st.write('## 桃園市 Youbike 站點地圖')

# 顯示更新時間
current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
st.write(f'**更新時間:** {current_time}')

# 計算下一次更新的時間
start_time = datetime.now()
end_time = start_time + timedelta(seconds=refresh_interval)

# 倒數計時進度條
progress_bar = st.progress(0)
status_text = st.empty()

# Function to fetch and create folium map
def create_map():
    # Load the Youbike data
    url = 'http://data.tycg.gov.tw/api/v1/rest/datastore/a1b4714b-3b75-4ff8-a8f2-cc377e4eaa0f?format=json&limit=200'
    Youbike_data_df = pd.read_json(url)
    Youbike_data_df = pd.DataFrame(Youbike_data_df['result']['records'])

    # Create the base map (centered around a point in Taoyuan)
    Taoyuan_map = folium.Map(location=[24.9935, 121.3010], zoom_start=12)

    # Create marker cluster
    marker_cluster = MarkerCluster().add_to(Taoyuan_map)

    for idx, row in Youbike_data_df.iterrows():
        # Check if latitude and longitude are valid
        try:
            lat = float(row['lat'])
            lng = float(row['lng'])
        except ValueError:
            continue

        # Set marker color based on 'sbi' value
        tot_value = int(row['sbi'])
        if tot_value == 0:
            color = 'red'
        elif 1 <= tot_value <= 3:
            color = 'orange'
        else:
            color = 'green'

        # Create a popup with responsive width
        popup_content = f"站點名稱: {row['sna']}, 總停車位: {row['tot']}, 可借車位: {row['sbi']}"
        popup = folium.Popup(popup_content, max_width=250)

        # Add marker to the cluster
        folium.Marker(
            location=[lat, lng],
            popup=popup,
            icon=folium.Icon(color=color)
        ).add_to(marker_cluster)

    return Taoyuan_map

# Generate and display the map
Taoyuan_map = create_map()
st_data = st_folium(Taoyuan_map, width=1200, height=500)

# 反轉進度條的更新
for i in range(refresh_interval):
    remaining_time = refresh_interval - i
    # 計算反向的進度
    progress = 1 - (i / refresh_interval)
    progress_bar.progress(progress)
    status_text.text(f"距離下一次更新：{remaining_time} 秒")
    time.sleep(1)

