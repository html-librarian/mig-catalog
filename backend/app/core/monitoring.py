"""
Модуль мониторинга и метрик
"""

import time

try:
    import psutil

    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    psutil = None
import gc
from collections import defaultdict
from typing import Any, Dict, List

from app.core.logging import get_logger

logger = get_logger("monitoring")


class PerformanceMonitor:
    """Монитор производительности приложения"""

    def __init__(self):
        self.start_time = time.time()
        self.request_counts = defaultdict(int)
        self.response_times = defaultdict(list)
        self.error_counts = defaultdict(int)
        self.last_cleanup = time.time()
        self.cleanup_interval = 3600  # 1 час

    def record_request(
        self,
        endpoint: str,
        method: str,
        status_code: int,
        response_time: float,
    ):
        """Записать метрику запроса"""
        key = f"{method}:{endpoint}"
        self.request_counts[key] += 1

        if status_code >= 400:
            self.error_counts[key] += 1
        # Сохраняем время ответа (максимум 1000 записей на эндпоинт)
        if len(self.response_times[key]) < 1000:
            self.response_times[key].append(response_time)
        # Очистка старых данных
        self._cleanup_old_data()

    def _cleanup_old_data(self):
        """Очистка старых данных"""
        current_time = time.time()
        if current_time - self.last_cleanup > self.cleanup_interval:
            for key in list(self.response_times.keys()):
                # Оставляем только последние 100 записей
                if len(self.response_times[key]) > 100:
                    self.response_times[key] = self.response_times[key][-100:]
            self.last_cleanup = current_time

    def get_metrics(self) -> Dict[str, Any]:
        """Получить метрики производительности"""
        current_time = time.time()
        uptime = current_time - self.start_time

        # Системные метрики
        if PSUTIL_AVAILABLE:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")
            system_metrics = {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_gb": memory.available / (1024**3),
                "disk_percent": disk.percent,
                "disk_free_gb": disk.free / (1024**3),
            }
        else:
            system_metrics = {
                "cpu_percent": 0,
                "memory_percent": 0,
                "memory_available_gb": 0,
                "disk_percent": 0,
                "disk_free_gb": 0,
                "note": "psutil not available",
            }

        # Метрики приложения
        total_requests = sum(self.request_counts.values())
        total_errors = sum(self.error_counts.values())
        error_rate = (
            (total_errors / total_requests * 100) if total_requests > 0 else 0
        )

        # Средние времена ответа
        avg_response_times = {}
        for key, times in self.response_times.items():
            if times:
                avg_response_times[key] = sum(times) / len(times)

        return {
            "system": {"uptime_seconds": uptime, **system_metrics},
            "application": {
                "total_requests": total_requests,
                "total_errors": total_errors,
                "error_rate_percent": error_rate,
                "requests_per_minute": self._calculate_rpm(),
                "avg_response_times": avg_response_times,
                "gc_stats": self._get_gc_stats(),
            },
            "endpoints": {
                "request_counts": dict(self.request_counts),
                "error_counts": dict(self.error_counts),
            },
        }

    def _calculate_rpm(self) -> float:
        """Рассчитать запросы в минуту"""
        current_time = time.time()
        uptime_minutes = (current_time - self.start_time) / 60
        total_requests = sum(self.request_counts.values())
        return total_requests / uptime_minutes if uptime_minutes > 0 else 0

    def _get_gc_stats(self) -> Dict[str, Any]:
        """Получить статистику сборщика мусора"""
        gc.collect()
        return {
            "objects": len(gc.get_objects()),
            "garbage": len(gc.garbage),
            "collections": gc.get_stats(),
        }


class HealthChecker:
    """Проверка здоровья системы"""

    def __init__(self):
        self.checks = {}
        self.last_check = {}
        self.last_results = {}  # Добавляем хранение результатов
        self.check_interval = 300  # 5 минут

    def register_check(self, name: str, check_func: callable):
        """Зарегистрировать проверку здоровья"""
        self.checks[name] = check_func

    def run_health_checks(self) -> Dict[str, Any]:
        """Запустить все проверки здоровья"""
        current_time = time.time()
        results = {
            "status": "healthy",
            "timestamp": current_time,
            "checks": {},
        }

        all_healthy = True

        for name, check_func in self.checks.items():
            # Проверяем, нужно ли запускать проверку
            if (
                name not in self.last_check
                or current_time - self.last_check[name] > self.check_interval
            ):
                try:
                    check_result = check_func()
                    self.last_check[name] = current_time

                    if isinstance(check_result, dict):
                        result_data = check_result
                    else:
                        status = "healthy" if check_result else "unhealthy"
                        result_data = {"status": status, "details": None}

                    # Сохраняем результат
                    self.last_results[name] = result_data
                    results["checks"][name] = result_data

                    if result_data["status"] != "healthy":
                        all_healthy = False

                except Exception as e:
                    logger.error(f"Health check {name} failed: {e}")
                    error_result = {"status": "unhealthy", "error": str(e)}
                    self.last_results[name] = error_result
                    results["checks"][name] = error_result
                    all_healthy = False
            else:
                # Используем кэшированный результат
                results["checks"][name] = self.last_results.get(
                    name, {"status": "unknown", "details": "Cached result"}
                )

        results["status"] = "healthy" if all_healthy else "unhealthy"
        return results


class AlertManager:
    """Менеджер алертов"""

    def __init__(self):
        self.alerts = []
        self.alert_thresholds = {
            "cpu_percent": 80,
            "memory_percent": 85,
            "disk_percent": 90,
            "error_rate": 5,
            "response_time": 2.0,  # секунды
        }

    def check_alerts(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Проверить метрики на предмет алертов"""
        new_alerts = []

        # Проверка CPU
        cpu_percent = metrics.get("system", {}).get("cpu_percent", 0)
        if cpu_percent > self.alert_thresholds["cpu_percent"]:
            new_alerts.append(
                {
                    "level": "warning",
                    "message": f"High CPU usage: {cpu_percent}%",
                    "metric": "cpu_percent",
                    "value": cpu_percent,
                    "threshold": self.alert_thresholds["cpu_percent"],
                }
            )

        # Проверка памяти
        memory_percent = metrics.get("system", {}).get("memory_percent", 0)
        if memory_percent > self.alert_thresholds["memory_percent"]:
            new_alerts.append(
                {
                    "level": "warning",
                    "message": f"High memory usage: {memory_percent}%",
                    "metric": "memory_percent",
                    "value": memory_percent,
                    "threshold": self.alert_thresholds["memory_percent"],
                }
            )

        # Проверка диска
        disk_percent = metrics.get("system", {}).get("disk_percent", 0)
        if disk_percent > self.alert_thresholds["disk_percent"]:
            new_alerts.append(
                {
                    "level": "critical",
                    "message": f"High disk usage: {disk_percent}%",
                    "metric": "disk_percent",
                    "value": disk_percent,
                    "threshold": self.alert_thresholds["disk_percent"],
                }
            )

        # Проверка ошибок
        error_rate = metrics.get("application", {}).get(
            "error_rate_percent", 0
        )
        if error_rate > self.alert_thresholds["error_rate"]:
            new_alerts.append(
                {
                    "level": "critical",
                    "message": f"High error rate: {error_rate}%",
                    "metric": "error_rate",
                    "value": error_rate,
                    "threshold": self.alert_thresholds["error_rate"],
                }
            )

        # Проверка времени ответа
        avg_response_times = metrics.get("application", {}).get(
            "avg_response_times", {}
        )
        for endpoint, response_time in avg_response_times.items():
            if response_time > self.alert_thresholds["response_time"]:
                new_alerts.append(
                    {
                        "level": "warning",
                        "message": (
                            f"Slow response time for {endpoint}: "
                            f"{response_time}s"
                        ),
                        "metric": "response_time",
                        "endpoint": endpoint,
                        "value": response_time,
                        "threshold": self.alert_thresholds["response_time"],
                    }
                )

        # Добавляем новые алерты
        for alert in new_alerts:
            alert["timestamp"] = time.time()
            self.alerts.append(alert)
            logger.warning(f"Alert: {alert['message']}")

        # Очищаем старые алерты (старше 24 часов)
        current_time = time.time()
        self.alerts = [
            alert
            for alert in self.alerts
            if current_time - alert["timestamp"] < 86400
        ]

        return new_alerts

    def get_alerts(self) -> List[Dict[str, Any]]:
        """Получить все активные алерты"""
        return self.alerts


# Глобальные экземпляры
performance_monitor = PerformanceMonitor()
health_checker = HealthChecker()
alert_manager = AlertManager()


def record_request_metrics(
    endpoint: str, method: str, status_code: int, response_time: float
):
    """Записать метрики запроса"""
    performance_monitor.record_request(
        endpoint, method, status_code, response_time
    )


def get_system_metrics() -> Dict[str, Any]:
    """Получить системные метрики"""
    return performance_monitor.get_metrics()


def get_health_status() -> Dict[str, Any]:
    """Получить статус здоровья системы"""
    return health_checker.run_health_checks()


def check_alerts() -> List[Dict[str, Any]]:
    """Проверить алерты"""
    metrics = get_system_metrics()
    return alert_manager.check_alerts(metrics)
