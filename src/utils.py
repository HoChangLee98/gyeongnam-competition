import requests
import numbers
import math
import numpy as np
from shapely import Polygon
import geopandas as gpd
import matplotlib.pyplot as plt
plt.rcParams["font.family"] = "Malgun Gothic"


def address2coordinate(
    address:str, 
    apiurl:str = "https://api.vworld.kr/req/address?", 
    apikey:str = "96DC019B-5E26-33AD-B6A9-9B4991045E75", 
    ) -> tuple:
    """주소를 경도(longitude), 위도(latitude)로 변환하는 함수

    Args:
        apiurl (str): v-world 사용 api 주소
        apikey (str): v-world 사용 api 인증키
        address (str): 경도, 위도로 변환하고자하는 주소
    Returns:
        tuple: 경도(longitude), 위도(latitude) 값
    """
    ## 요청파라미터
    params = {
        "service": "address",
        "request": "getcoord",
        "crs": "epsg:4326",
        "address": address,
        "format": "json",
        "type": "road",
        "key": apikey
    }

    ## 결과응답
    response = requests.get(apiurl, params=params)
    
    ## 에러가 없을 경우 결과응답으로부터 경도(longitude), 위도(latitude) 추출
    if response.status_code == 200:
        longitude = response.json()["response"]["result"]["point"]["x"]
        latitude = response.json()["response"]["result"]["point"]["y"]
    else:
        print("Error") 
        
    return longitude, latitude


class GeoUtil:
    """
    Geographical Utils
    """
    @staticmethod
    def degree2radius(degree):
        return degree * (math.pi/180)
    
    @staticmethod
    def get_harversion_distance(x1, y1, x2, y2, round_decimal_digits=5):
        """
        경위도 (x1,y1)과 (x2,y2) 점의 거리를 반환
        Harversion Formula 이용하여 2개의 경위도간 거래를 구함(단위:Km)
        """
        if x1 is None or y1 is None or x2 is None or y2 is None:
            return None
        assert isinstance(x1, numbers.Number) and -180 <= x1 and x1 <= 180
        assert isinstance(y1, numbers.Number) and  -90 <= y1 and y1 <=  90
        assert isinstance(x2, numbers.Number) and -180 <= x2 and x2 <= 180
        assert isinstance(y2, numbers.Number) and  -90 <= y2 and y2 <=  90

        R = 6371 # 지구의 반경(단위: km)
        dLon = GeoUtil.degree2radius(x2-x1)    
        dLat = GeoUtil.degree2radius(y2-y1)

        a = math.sin(dLat/2) * math.sin(dLat/2) \
            + (math.cos(GeoUtil.degree2radius(y1)) \
              *math.cos(GeoUtil.degree2radius(y2)) \
              *math.sin(dLon/2) * math.sin(dLon/2))
        b = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return round(R * b, round_decimal_digits)

    @staticmethod
    def get_euclidean_distance(x1, y1, x2, y2, round_decimal_digits=5):        
        """
        유클리안 Formula 이용하여 (x1,y1)과 (x2,y2) 점의 거리를 반환
        """
        if x1 is None or y1 is None or x2 is None or y2 is None:
            return None
        assert isinstance(x1, numbers.Number) and -180 <= x1 and x1 <= 180
        assert isinstance(y1, numbers.Number) and  -90 <= y1 and y1 <=  90
        assert isinstance(x2, numbers.Number) and -180 <= x2 and x2 <= 180
        assert isinstance(y2, numbers.Number) and  -90 <= y2 and y2 <=  90

        dLon = abs(x2-x1) # 경도 차이
        if dLon >= 180:   # 반대편으로 갈 수 있는 경우
            dLon -= 360   # 반대편 각을 구한다
        dLat = y2-y1      # 위도 차이
        return round(math.sqrt(pow(dLon,2)+pow(dLat,2)),round_decimal_digits)
    
    
class VisualGeoData:
    def __init__(
        self, 
        bnd_count:gpd, 
        silver_index_bot20_within_bnd:gpd, 
        facility_index_bot20_within_bnd:gpd
    ):
        self.bnd_count = bnd_count
        self.silver_index_bot20_within_bnd = silver_index_bot20_within_bnd
        self.facility_index_bot20_within_bnd = facility_index_bot20_within_bnd

    def visualize_by_counts(
        self, 
        column:str="silver_ADM_count",
        figsize:tuple=(20, 20),
        legend:bool=True, 
        cmap:str='OrRd', 
        edgecolor:str='black', 
        linewidth:float=0.5,
        title_fontsize:int=20,
        title_name:str=None, 
    ):
        """읍면동 혹은 시군구 별로 하위 20% 지역의 수를 세고 수에 따라 시각화하는 함수

        Args:
            column (str, optional): 
                표현하고자하는 변수. 
                읍면동 별 노인 중심점일 경우: silver_ADM_count
                시군구 별 노인 중심점일 경우: silver_SGG_count
                읍면동 별 시설 위치일 경우  : facility_ADM_count
                시군구 별 시설 위치일 경우  : facility_SGG_count
                "silver_ADM_count", Defaults to "silver_ADM_count".
                
            figsize (tuple, optional): For figure size. Defaults to (20, 20).
            legend (bool, optional): Decision for legend. Defaults to True.
            cmap (str, optional): Color. Defaults to 'OrRd'.
            edgecolor (str, optional): Egde color. Defaults to 'black'.
            linewidth (float, optional): Line size for boundary. Defaults to 0.5.
            title_fontsize (int, optional): Set title fontsize. Defaults to 20.
            title_name (str, optional): Set title name. Defaults to None.
        """        
        if column in ["facility_ADM_count", "facility_SGG_count"]:
            cmap = "BuPu"
            
        # 시각화
        fig, ax = plt.subplots(1, 1, figsize=figsize)

        # 읍면동 별 취약 지역 수를 컬러맵으로 시각화
        self.bnd_count.plot(
            column=column, 
            ax=ax, 
            legend=legend,
            cmap=cmap, 
            edgecolor=edgecolor, 
            linewidth=linewidth
            )

        # 검은색 배경 설정 (옵션)
        fig.patch.set_facecolor('black')
        ax.set_facecolor('black')

        plt.title(title_name, color='white', fontsize=title_fontsize)
        plt.show()
        

    def create_grid(
        self,
        gdf:gpd, 
        grid_size:float=100
        ):
        """_summary_

        Args:
            gdf (geopandas): Geopandas for boundary
            grid_size (float): Grid size

        Returns:
            gpd: GeoPandas for grid
        """        
        bounds = gdf.total_bounds
        xmin, ymin, xmax, ymax = bounds
        rows = int(np.ceil((ymax - ymin) / grid_size))
        cols = int(np.ceil((xmax - xmin) / grid_size))
        
        x_left_origin = xmin
        x_right_origin = xmin + grid_size
        y_top_origin = ymax
        y_bottom_origin = ymax - grid_size
        polygons = []
        
        for i in range(cols):
            y_top = y_top_origin
            y_bottom = y_bottom_origin
            for j in range(rows):
                polygons.append(Polygon([(x_left_origin, y_top), 
                                        (x_right_origin, y_top), 
                                        (x_right_origin, y_bottom), 
                                        (x_left_origin, y_bottom)])) 
                y_top = y_top - grid_size
                y_bottom = y_bottom - grid_size
            x_left_origin = x_left_origin + grid_size
            x_right_origin = x_right_origin + grid_size

        grid = gpd.GeoDataFrame({'geometry':polygons})
        return grid

    
    def visualize_by_index(
        self, 
        how:str,
        on:str,
        cityname:str,
        grid_size:float=250,
        index_method:str="reverse", 
        figsize:tuple=(12, 12), 
        legend:bool=True,
        cmap:str="OrRd", 
        grid_linewith:float=0.2, 
        city_linewith:float=1, 
        title_name:str=None, 
        title_fontsize:float=15        
    ):
        """한 읍면동 혹은 시군구 내에 노인 중심점 혹은 시설 위치에 대한 지수를 시각화하는 함수

        Args:
            how (str): 읍면동 혹은 시군구별로 할지 선택. "emd", "sgg"
            on (str): 노인 중심점 혹은 시설로 할지 선택. "silver", "facility"
            cityname (str): 읍면동이라면 읍면동 중 하나의 지역 선택, 시군구라면 시군구 중 하나의 지역 선택
            grid_size (float, optional): Set grid size. Defaults to 250.
            index_method (str, optional): Choose index method. "reverse", "reverse_log" Defaults to "reverse".
            figsize (tuple, optional): Set figure size. Defaults to (12, 12).
            legend (bool, optional): Boolean of legend. Defaults to True.
            cmap (str, optional): Color . Defaults to "OrRd".
            grid_linewith (float, optional): Set grid line size. Defaults to 0.2.
            city_linewith (float, optional): Set city line size. Defaults to 1.
            title_name (str, optional): Set title name. Defaults to None.
            title_fontsize (float, optional): Set title fontsize. Defaults to 15.
        """        

        if how == "emd":
            col_NM = "ADM_NM"
        elif how == "sgg":
            col_NM = "시군구명"
        
        if on == "silver": 
            index_bot20_within_bnd = self.silver_index_bot20_within_bnd
        elif on == "facility":
            cmap = "BuPu"
            index_bot20_within_bnd = self.facility_index_bot20_within_bnd
        
        ## 지역 설정            
        index_bot20_within_bnd = index_bot20_within_bnd[index_bot20_within_bnd[col_NM] == cityname]
        bnd_ = self.bnd_count[self.bnd_count[col_NM] == cityname]
        
        ## grid 그리기
        grid_size = grid_size  # 100 meters
        grid = self.create_grid(bnd_, grid_size)
        
        # 격자와 지리 데이터 병합
        grid.crs = bnd_.crs  # 좌표계 맞추기
        grid = gpd.sjoin(grid, bnd_[["geometry", "ADM_NM"]], how='inner', predicate='intersects')
        grid = grid.drop(columns=["index_right"])
        points_within_grid = gpd.sjoin(
            index_bot20_within_bnd, 
            grid, 
            how='inner', 
            predicate='within'
            )
        
        ## 지수 설정 방법
        if index_method == "reverse":
            points_within_grid["total_idx_reverse"] = 1 / points_within_grid["total_idx"]
        elif index_method == "reverse_log":
            points_within_grid["total_idx_reverse"] = np.log1p(1 / points_within_grid["total_idx"])
           
        ## 그리드에 속하는 지수 합치기 
        grid_idx_sum_reverse = points_within_grid.groupby('index_right')["total_idx_reverse"].sum()
        grid['idx_sum_reverse'] = grid_idx_sum_reverse
        
        ## 그림
        fig, ax = plt.subplots(1, 1, figsize=figsize)

        # 검은색 배경 설정 (옵션)
        fig.patch.set_facecolor('black')
        ax.set_facecolor('black')

        # 격자별 total_idx를 컬러맵으로 시각화
        grid.plot(
            column="idx_sum_reverse", 
            ax=ax, 
            legend=legend, 
            cmap=cmap
            )
        grid.boundary.plot(ax=ax, linewidth=grid_linewith, color='white')
        bnd_.boundary.plot(ax=ax, linewidth=city_linewith, color='white')

        # 제목 설정
        plt.title(title_name, color='white', fontsize=title_fontsize) 
        plt.show()