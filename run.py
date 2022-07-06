# -*- coding=utf-8 -*-

import flask, json
from flask import request
import io
import re
from utils import query
from map import CoordinateTransform
server =flask.Flask(__name__)
glob_msg=None
@server.route('/msg', methods=['get', 'post'])
def msg():
    if request.method == "POST":
        #短信内容
        data=request.form.to_dict()
        typeinfo = data['type']
        try:
            _id = int(data['id'])
        except:
            _id = 0
        #地图中心默认在三机房
        center=[118.23692321777344,33.95806235991365]
        if typeinfo=="kanfuinfo":
            print("kanfu")
            sql = "select * from kanfuinfo"
            datainfo=[]
            res = query(sql)
            for obj in res:
                objdata={"_id":obj[0],"kanfuname":obj[1],"company":obj[3],"display":[{"name":"县区","value":obj[2]},{"name":"责任人","value":obj[4]},{"name":"电话","value":obj[5]}]}
                datainfo.append(objdata) 
            resu = {'code': 200, 'message': '成功',"data":datainfo}
            #print(resu)
            return json.dumps(resu, ensure_ascii=False)
        elif typeinfo=="point":
            print("point")
            codedict={"LR":"WF001","PL":"NW001","XN":"NW001","ND":"NW001"}
            datalist=[]
            #采集面积图数据
            try:
                pointtype='LR'
                sql = "select * from kanhudata where kanfuid={} and pointtype='{}'".format(_id,pointtype)
                datadic={}
                datainfo=[]
                res = query(sql)
                for obj in res:
                    #objdata={"sequid":obj[2],"lat":obj[3],"log":obj[4],"pointtype":obj[5],"name":obj[6]}
                    objdata=cdt.wgs84_to_gcj02(obj[4], obj[3])
                    #objdata=[obj[4],obj[3]]
                    datainfo.append(objdata)
                datadic['_id']="{}{:0>3d}{:0>7d}".format(pointtype,_id,int(obj[2]))
                datadic["name"]="湖体"
                datadic["geometry"]={"type": "Polygon","coordinates":[datainfo]}
                datadic["code"]="{}-{}{:0>3d}{:0>5d}".format(codedict[pointtype],pointtype,_id,int(obj[2]))
                datadic["category"]= pointtype
                datalist.append(datadic)
            except:
                pass
            #采集mark点数据
            pointtype='XN'
            sql = "select * from kanhudata where kanfuid={} and pointtype='{}'".format(_id,pointtype)           
            res = query(sql)
            for obj in res:
                datadic={}
                datadic["name"]=obj[6]
                datadic['_id']="{}{:0>3d}{:0>7d}".format(pointtype,_id,int(obj[2]))
                #datadic["geometry"]={"type": "Point","coordinates":[obj[4],obj[3]]}
                datadic["geometry"]={"type": "Point","coordinates":cdt.wgs84_to_gcj02(obj[4], obj[3])}
                datadic["code"]="{}-{}{:0>3d}{:0>5d}".format(codedict[pointtype],pointtype,_id,int(obj[2]))
                datadic["category"]= pointtype
                datalist.append(datadic)
            print(len(datalist))
            #采集小球点数据
            try:
                pointtype='ND'
                sql = "select * from kanhudata where kanfuid={} and pointtype='{}'".format(_id,pointtype)      
                res = query(sql)
                for obj in res:
                    datadic={}
                    datadic["name"]="{}-{:0>3d}{:0>7d}".format(pointtype,_id,int(obj[2]))
                    datadic['_id']="{}{:0>3d}{:0>7d}".format(pointtype,_id,int(obj[2]))
                    #datadic["geometry"]={"type": "Point","coordinates":[obj[4],obj[3]]}
                    datadic["geometry"]={"type": "Point","coordinates":cdt.wgs84_to_gcj02(obj[4], obj[3])}
                    datadic["code"]="{}-{}{:0>3d}{:0>5d}".format(codedict[pointtype],pointtype,_id,int(obj[2]))
                    datadic["category"]= pointtype
                    datalist.append(datadic)
                print(len(datalist))
            except:
                pass
            #####################################################################
             #采集运动轨迹数据
            pointtype='PL'
            sql = "select * from kanhudata where kanfuid={} and pointtype='{}'".format(_id,pointtype)          
            res = query(sql)
            i=0
            log=0.0
            lat=0.0
            for obj in res:
                if(i==0):
                    log=obj[4]
                    lat=obj[3]
                    center=cdt.wgs84_to_gcj02(log,lat)
                    i+=1
                else:
                    datadic={}
                    datadic["name"]="{}-{:0>3d}{:0>7d}".format(pointtype,_id,int(obj[2]))
                    datadic['_id']="{}{:0>3d}{:0>7d}".format(pointtype,_id,int(obj[2]))
                    #datadic["geometry"]={"type": "LineString","coordinates":[[log,lat],[obj[4],obj[3]]]}
                    datadic["geometry"]={"type": "LineString","coordinates":[cdt.wgs84_to_gcj02(log,lat),cdt.wgs84_to_gcj02(obj[4], obj[3])]}
                    datadic["code"]="{}-{}{:0>3d}{:0>5d}".format(codedict[pointtype],pointtype,_id,int(obj[2]))
                    datadic["category"]= pointtype
                    #print(datadic)
                    datalist.append(datadic)
                    i+=1
                    log=obj[4]
                    lat=obj[3]
            #####################################################################
            #print(len(datalist))
            #print(datalist)
            resu = {'code': 200, 'message': '成功',"data":datalist,"center":center}
            #print(resu)
            return json.dumps(resu, ensure_ascii=False)
        else:
            return  json.dumps({'code': 400, 'message': '失败',"data":"失败"}, ensure_ascii=False)
        
    elif request.method == "GET":
        pass

if __name__ == '__main__':
    cdt = CoordinateTransform()
    server.run(port=45353, host='192.168.0.198')
#    cdt = CoordinateTransform()
#    lng_lat = input(f"请输入经纬度坐标:").strip().strip('\n').split(',')
#    lng, lat = lng_lat[0], lng_lat[-1]
#    print(f"原始经纬度坐标:{lng},{lat}")
#    print(f"转为bd09坐标系:{cdt.gcj02_to_bd09(float(lng), float(lat))}")
#    print(f"转为wgs84坐标系:{cdt.gcj02_to_wgs84(float(lng), float(lat))}")
#    mer_coord = cdt.lonLat2Mercator(float(lng), float(lat))
#    print(f"转为墨卡托坐标:{mer_coord}")
#    print(f"高德瓦片坐标:{cdt.wmc2tile(mer_coord[0], mer_coord[-1])}")
