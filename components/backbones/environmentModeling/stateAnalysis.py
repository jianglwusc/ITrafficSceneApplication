from .eModel import eModel
from ..base import BaseBackboneComponent
from ..registry import BACKBONE_COMPONENT
from .tools import get_centre, projection, vLen
import math
from utils.utils import identify_number_plate,get_current_time

@BACKBONE_COMPONENT.register_module
class stateAnalysis(BaseBackboneComponent):
    def __init__(self, eModelPath):
        eM = eModel.load(eModelPath)
        self.mainMask = eM.sMap.getMainMask()
        self.stopLine = eM.sMap.getStopLine()
        self.avgBbox = eM.sMap.avgBbox
        self.mainAxis = eM.sMap.mainAxis
        if self.mainAxis > 0:
            self.mainAxis -= math.pi
        self.classes = ['car', 'bus', 'truck']
        self.objDict = {}
        self.passCount = 0

    def dotByStopLine(self, dot:list):
        k, b = self.stopLine
        if k*dot[0] + b - dot[1] > self.avgBbox/4:
            return 1
        elif k*dot[0] + b - dot[1] < -self.avgBbox/4:
            return -1
        else:
            return 0
    
    def appropriatePhoto(self, dot:list):
        k, b = self.stopLine
        if -self.avgBbox*1.5 < k*dot[0] + b - dot[1] < self.avgBbox*1.5:
            return True
        else:
            return True
     
    def dotInMainMask(self, dot:list):
        return self.mainMask[int(dot[1]), int(dot[0])] != 0

    def inputObj(self, img, obj):
        returnInfo = None
        # 过滤掉不在检测范围内的目标
        if obj['cls_pred'] not in self.classes:
            return
        
        id = obj['id']
        centre = get_centre(obj['bbox'])
        # 初始化第一次出现的目标
        if id not in self.objDict.keys():
            self.objDict[id] = {
                'id':id,
                'maybe_classes':{obj['cls_pred']: 1},
                'path':[centre],
                'passState': self.dotByStopLine(centre),
                'number_plate': None,
            }
            return
        # 更新已有目标：
        
        # 1.拍照检测：
        # 仅检测合适拍照且没有拍照且速度方向正确的目标
        number_plate = None
        if self.appropriatePhoto(centre) and self.objDict[id]['number_plate'] is None:
            # todo:拍照识别
            bbox = [
                int(obj['bbox'][0]),
                int(obj['bbox'][1]),
                int(obj['bbox'][2]),
                int(obj['bbox'][3])
            ]
            number_plate = identify_number_plate(img, bbox=bbox)
            if number_plate is not None:
                self.objDict[id]['number_plate'] = number_plate
        # 2.过线检测：
        passState = self.dotByStopLine(centre)
        cls_name = max(self.objDict[id]['maybe_classes'], key=self.objDict[id]['maybe_classes'].get)
        lastPassState = self.objDict[id]['passState']
        if passState == 1 and lastPassState == -1 and cls_name in self.classes:      # 只检测由-1 到 1 的跳变
            self.objDict[id]['passState'] = passState
            returnInfo = {'info_type': 'pass'}
            returnInfo['id'] = id
            returnInfo['start_time'] = get_current_time()
            returnInfo['end_time'] = get_current_time()
            returnInfo['passage_type'] = None
            returnInfo['obj_type'] = cls_name
            returnInfo['number_plate'] = self.objDict[id]['number_plate']
            self.passCount += 1
            print('ID为：' + str(id) + cls_name + '的车辆过线，计数器加一，PassCount' + str(self.passCount))
            #print(returnInfo)
            return returnInfo

        # 3. 数据更新：
        self.objDict[id]['path'].append(centre)
        cls_pred = obj['cls_pred']
        if cls_pred not in self.objDict[id]['maybe_classes']:
            self.objDict[id]['maybe_classes'][cls_pred] = 0
        self.objDict[id]['maybe_classes'][cls_pred] += 1

    def analysis(self, img, img_info):
        img_info['analysis'] = []
        objs = img_info['objects']
        # 新目标添加统计
        for obj in objs:
            returnInfo = self.inputObj(img, obj)
            if returnInfo is not None:
                img_info['analysis'].append(returnInfo)
                # print(img_info['analysis'])
        img_info['pass_count'] = self.passCount

    def process(self, **kwargs):
        imgs_info = kwargs['imgs_info']
        imgs = kwargs['imgs']
        for i in range(len(imgs_info)):
            #print('正在处理第'+ str(img_info['index']) + '张图片：')
            self.analysis(imgs[i],imgs_info[i]) 
        return kwargs