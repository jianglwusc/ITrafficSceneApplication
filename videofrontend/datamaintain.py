from videofrontend.dao.carsvolumedao import CarsVolumeDao
from videofrontend.dao.vehicleviolationdao import VehicleViolationDao


class DataMaintenance(object):
    # 车流量Dao
    car_volume_dao = CarsVolumeDao()
    # 折线图历史数据
    line_chart_datas = []
    vehicle_volume_dao=VehicleViolationDao()
    #场景编号，1，2，3，4
    scene_number= '-1'
    @staticmethod
    def init_data():
        """
        初始化数据
        :return:
        """
        DataMaintenance.car_volume_dao.reset_all_traffic_volume_statistics()
        DataMaintenance.line_chart_datas.clear()
        DataMaintenance.vehicle_volume_dao.rset_vehicle_violation_statistics()
        DataMaintenance.scene_number='-1'

