from signals.live_signals import get_live_signals


class SignalService:

    @staticmethod
    def latest_signals():

        return get_live_signals()
