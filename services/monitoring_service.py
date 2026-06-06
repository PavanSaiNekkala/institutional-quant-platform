from monitoring.system_health_monitor import SystemHealthMonitor


class MonitoringService:

    @staticmethod
    def health_status():

        monitor = SystemHealthMonitor()

        return monitor.get_status()
