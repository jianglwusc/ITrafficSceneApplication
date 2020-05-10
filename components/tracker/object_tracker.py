from .sort import Sort
from .base import BaseTracker
from .registry import TRACKER
from components.detector.yolov3 import load_classes
import numpy as np

@TRACKER.register_module
class SORT_Track(BaseTracker):
    def __init__(self):
        BaseTracker.__init__(SORT_Track)
        self.tracker = Sort()
    
    def preprocessing(self, img_info):
        """跟踪模块预处理函数
        取出当前img_info中 key = 'objects' 部分中所有的 'bbox' 整合成一个 n*4 的数组
        Arguments:
            img_info {ditc} --  当前帧信息字典

        Returns:
            bboxs {np.narray} -- 重写img_info['objects']，添加 id 属性后返回
        """
        bboxs = []
        for obj in img_info['objects']:
            bboxs.append(obj['bbox'])
        bboxs = np.array(bboxs)
        return bboxs

    def track(self, bboxs=None):
        """跟踪函数
        Arguments:
            bboxs {np.narray} -- [description]
        Returns:
            bbox_ids {list} -- 添加了id号码的bboxs框，格式为[x1,y1,x2,y2,id]
            id_index {dict} -- id号和传入参数bboxs下标的对应关系, 转换格式方式为 id_index[id] = bboxs
            del_id {list} -- 在当前帧被删除的id，此id在之后的数据中都不会再出现
        """
        return self.tracker.update(bboxs)

    def afterprocessing(self, img_info, bbox_ids, id_index, del_id):
        """跟踪模块后处理函数
        Arguments:
            bbox_ids {list} -- 添加了id号码的bboxs框，格式为[x1,y1,x2,y2,id]
            id_index {dict} -- id号和传入参数bboxs下标的对应关系
            del_id {list} -- 在当前帧被删除的id，此id在之后的数据中都不会再出现
            img_info {dict} -- 略
        Returns:
            img_info {dict} -- 修改其 'object' 中的bboxs组件，使之变得更顺滑，添加 id 属性，
        注：在该模块中可能会删除某些object
        """
        objs = []
        for bbox_id in bbox_ids:
            id = bbox_id[4]        # id号
            bbox = bbox_id[0:4]    # 平滑处理后的bbox框
            index = int(id_index[id])
            obj = img_info['objects'][index]
            obj['bbox'] = bbox
            obj['id'] = id
            objs.append(obj)
        # 更新img_info 的objects
        img_info['objects'] = objs
        #print(objs)

        # 为img_info 添加当前帧中消失的目标：
        img_info['del_id'] = del_id
        #print(del_id)

        return img_info

    def __call__(self, img_info=None):
        """Sort跟踪模块接口
        Arguments:
            img_info {dict} -- 略
        """
        # 如果img_info缺少关键数据则返回原数据
        if 'objects' not in img_info.keys():
             print('cant found \'objects\' in img_info')
             print(img_info)
             return img_info

        bboxs = self.preprocessing(img_info)
        bbox_ids, id_index, del_id = self.track(bboxs)
        return self.afterprocessing(img_info, bbox_ids,id_index, del_id)

