# 智慧交通场景应用

   * [智慧交通场景应用](#智慧交通场景应用)
      * [简介](#简介)
         * [支持功能](#支持功能)
      * [主要特点](#主要特点)
      * [部署](#部署)

## 简介

​		基于计算机视觉技术实现的，支持多种交通场景下的自动车道环境建模以及车流量，违章停车，违章占用车道监测。

### 支持功能

- [x] 过往车辆的流量统计 
- [ ] 车速检测 
- [ ] 路口交通的饱和度以及拥堵情况
- [ ] 闯红灯的机动车检测 
- [ ] 不礼让行人检测
- [x] 机动车违章停车监测 
- [x] 违法占用车道检测 
- [x] 车牌识别 

## 主要特点

- 模块化设计，支持自定义组件，支持自定义构建视频处理Task
- 并行设计，Task中的各个模块采取多进程并行设计
- 简易部署，支持Docker部署进行开发或使用

## 部署

​		自行查看doc文件夹中的部署说明书

## 配套前端
- [前端项目](https://github.com/SDGLBL/itsa-web)
