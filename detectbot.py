"""Python Crypto Bot consuming Coinbase Pro or Binance APIs"""

import logging
import os
import sched
import sys
import time
import pandas as pd
from datetime import datetime
from models.PyCryptoBot import PyCryptoBot
from models.AppState import AppState
from models.Trading import TechnicalAnalysis
from models.TradingAccount import TradingAccount
from models.helper.MarginHelper import calculate_margin
from views.TradingGraphs import TradingGraphs

# production: disable traceback
# sys.tracebacklimit = 0

app = PyCryptoBot()
state = AppState()

s = sched.scheduler(time.time, time.sleep)

config = {}
account = None
if app.getLastAction() != None:
    state.last_action = app.getLastAction()

    account = TradingAccount(app)

# if live trading is enabled
elif app.isLive():
    # connectivity check
    if app.getTime() is None:
        raise ConnectionError(
            'Unable to start the bot as your connection to the exchange is down. Please check your Internet connectivity!')

    account = TradingAccount(app)

    state.last_action = "SELL"

    if app.getExchange() == 'binance':
        if state.last_action == 'SELL' and account.getBalance(app.getQuoteCurrency()) < 0.001:
            raise Exception('Insufficient available funds to place buy order: ' + str(account.getBalance(
                app.getQuoteCurrency())) + ' < 0.1 ' + app.getQuoteCurrency() + "\nNote: A manual limit order places a hold on available funds.")
        elif state.last_action == 'BUY' and account.getBalance(app.getBaseCurrency()) < 0.001:
            raise Exception('Insufficient available funds to place sell order: ' + str(account.getBalance(
                app.getBaseCurrency())) + ' < 0.1 ' + app.getBaseCurrency() + "\nNote: A manual limit order places a hold on available funds.")

    elif app.getExchange() == 'coinbasepro':
        if state.last_action == 'SELL' and account.getBalance(app.getQuoteCurrency()) < 50:
            raise Exception('Insufficient available funds to place buy order: ' + str(account.getBalance(
                app.getQuoteCurrency())) + ' < 50 ' + app.getQuoteCurrency() + "\nNote: A manual limit order places a hold on available funds.")
        elif state.last_action == 'BUY' and account.getBalance(app.getBaseCurrency()) < 0.001:
            raise Exception('Insufficient available funds to place sell order: ' + str(account.getBalance(
                app.getBaseCurrency())) + ' < 0.1 ' + app.getBaseCurrency() + "\nNote: A manual limit order places a hold on available funds.")


def getAction(now: datetime = datetime.today().strftime('%Y-%m-%d %H:%M:%S'), app: PyCryptoBot = None, price: float = 0,
              df: pd.DataFrame = pd.DataFrame(), df_last: pd.DataFrame = pd.DataFrame(), last_action: str = 'WAIT',
              debug: bool = False) -> str:
    ema12gtema26co = bool(df_last['ema12gtema26co'].values[0])
    macdgtsignal = bool(df_last['macdgtsignal'].values[0])
    goldencross = bool(df_last['goldencross'].values[0])
    obv_pc = float(df_last['obv_pc'].values[0])
    elder_ray_buy = bool(df_last['eri_buy'].values[0])
    ema12gtema26 = bool(df_last['ema12gtema26'].values[0])
    macdgtsignalco = bool(df_last['macdgtsignalco'].values[0])
    ema12ltema26co = bool(df_last['ema12ltema26co'].values[0])
    macdltsignal = bool(df_last['macdltsignal'].values[0])


    print(f'ema12gtema26: {ema12gtema26}')
    print(f'ema12gtema26co: {ema12gtema26co}')
    print(f'macdgtsignalco: {macdgtsignalco}')
    if not app.disableBuyMACD():
        print(f'macdgtsignal: {macdgtsignal}')
    if not app.disableBullOnly():
        print(f'goldencross: {goldencross}')
    if not app.disableBuyOBV():
        print(f'obv_pc: {obv_pc} > -5')
    if not app.disableBuyElderRay():
        print(f'elder_ray_buy: {elder_ray_buy}')

    # criteria for a buy signal
    if ema12gtema26co is True \
            and (macdgtsignal is True or app.disableBuyMACD()) \
            and (goldencross is True or app.disableBullOnly()) \
            and (obv_pc > -5 or app.disableBuyOBV()) \
            and (elder_ray_buy is True or app.disableBuyElderRay()) \
            and last_action != 'BUY':

        if debug is True:
            print('*** Buy Signal ***')
            print(f'ema12gtema26co: {ema12gtema26co}')
            print(f'ema12gtema26: {ema12gtema26}')
            print(f'macdgtsignalco: {macdgtsignalco}')
            if not app.disableBuyMACD():
                print(f'macdgtsignal: {macdgtsignal}')
            if not app.disableBullOnly():
                print(f'goldencross: {goldencross}')
            if not app.disableBuyOBV():
                print(f'obv_pc: {obv_pc} > -5')
            if not app.disableBuyElderRay():
                print(f'elder_ray_buy: {elder_ray_buy}')
            print(f'last_action: {last_action}')

        # if disabled, do not buy within 3% of the dataframe close high
        if app.disableBuyNearHigh() is True and (price > (df['close'].max() * 0.97)):
            state.action = 'WAIT'

            log_text = str(now) + ' | ' + app.getMarket() + ' | ' + \
                app.printGranularity() + ' | Ignoring Buy Signal (price ' + str(price) + ' within 3% of high ' + str(
                df['close'].max()) + ')'
            print(log_text, "\n")
            logging.warning(log_text)

        return 'BUY'

    elif ema12gtema26 is True \
            and macdgtsignalco is True \
            and (goldencross is True or app.disableBullOnly()) \
            and (obv_pc > -5 or app.disableBuyOBV()) \
            and (elder_ray_buy is True or app.disableBuyElderRay()) \
            and last_action != 'BUY':

        if debug is True:
            print('*** Buy Signal ***')
            print(f'ema12gtema26: {ema12gtema26}')
            print(f'macdgtsignalco: {macdgtsignalco}')
            if not app.disableBullOnly():
                print(f'goldencross: {goldencross}')
            if not app.disableBuyOBV():
                print(f'obv_pc: {obv_pc} > -5')
            if not app.disableBuyElderRay():
                print(f'elder_ray_buy: {elder_ray_buy}')
            print(f'last_action: {last_action}')

        # if disabled, do not buy within 3% of the dataframe close high
        if app.disableBuyNearHigh() is True and (price > (df['close'].max() * 0.97)):
            state.action = 'WAIT'

            log_text = str(now) + ' | ' + app.getMarket() + ' | ' + \
                app.printGranularity() + ' | Ignoring Buy Signal (price ' + str(price) + ' within 3% of high ' + str(
                df['close'].max()) + ')'
            print(log_text, "\n")
            logging.warning(log_text)

        return 'BUY'

    # criteria for a sell signal
    elif ema12ltema26co is True \
            and (macdltsignal is True or app.disableBuyMACD()) \
            and last_action not in ['', 'SELL']:

        if debug is True:
            print('*** Sell Signal ***')
            print(f'ema12ltema26co: {ema12ltema26co}')
            print(f'macdltsignal: {macdltsignal}')
            print(f'last_action: {last_action}')

        return 'SELL'

    return 'WAIT'


def getInterval(df: pd.DataFrame = pd.DataFrame(), app: PyCryptoBot = None, iterations: int = 0) -> pd.DataFrame:
    if len(df) == 0:
        return df

    if app.isSimulation() and iterations > 0:
        # with a simulation iterate through data
        return df.iloc[iterations - 1:iterations]
    else:
        # most recent entry
        return df.tail(1)

def executeJob(sc, app=PyCryptoBot(), state=AppState(), trading_data=pd.DataFrame()):
    """Trading bot job which runs at a scheduled interval"""

    # connectivity check (only when running live)
    if app.isLive() and app.getTime() is None:
        print('Your connection to the exchange has gone down, will retry in 1 minute!')

        # poll every 5 minute
        list(map(s.cancel, s.queue))
        s.enter(300, 1, executeJob, (sc, app, state))
        return
    binance_coin_pairs = ['VENBNB', 'YOYOBNB', 'POWRBNB', 'NULSBNB', 'RCNBNB', 'RDNBNB', 'DLTBNB', 'WTCBNB', 'AMBBNB', 'BCCBNB', 'BATBNB', 'BCPTBNB', 'NEOBNB', 'QSPBNB', 'BTSBNB', 'XZCBNB', 'LSKBNB', 'IOTABNB', 'ADXBNB', 'CMTBNB', 'XLMBNB', 'CNDBNB', 'WABIBNB', 'LTCBNB', 'WAVESBNB', 'GTOBNB', 'ICXBNB', 'OSTBNB', 'AIONBNB', 'NEBLBNB', 'BRDBNB', 'MCOBNB', 'NAVBNB', 'TRIGBNB', 'APPCBNB', 'RLCBNB', 'PIVXBNB', 'STEEMBNB', 'NANOBNB', 'VIABNB', 'BLZBNB', 'AEBNB', 'RPXBNB', 'NCASHBNB', 'POABNB', 'ZILBNB', 'ONTBNB', 'STORMBNB', 'QTUMBNB', 'XEMBNB', 'WANBNB', 'SYSBNB', 'QLCBNB', 'ADABNB', 'GNTBNB', 'LOOMBNB', 'BCNBNB', 'REPBNB', 'TUSDBNB', 'ZENBNB', 'SKYBNB', 'EOSBNB', 'CVCBNB', 'THETABNB', 'XRPBNB', 'AGIBNB', 'NXSBNB', 'ENJBNB', 'TRXBNB', 'ETCBNB', 'SCBNB', 'NASBNB', 'MFTBNB', 'ARDRBNB', 'VETBNB', 'POLYBNB', 'PHXBNB', 'GOBNB', 'PAXBNB', 'RVNBNB', 'DCRBNB', 'USDCBNB', 'MITHBNB', 'RENBNB', 'BTTBNB', 'ONGBNB', 'HOTBNB', 'ZRXBNB', 'FETBNB', 'XMRBNB', 'ZECBNB', 'IOSTBNB', 'CELRBNB', 'DASHBNB', 'OMGBNB', 'MATICBNB', 'ATOMBNB', 'PHBBNB', 'TFUELBNB', 'ONEBNB', 'FTMBNB', 'ALGOBNB', 'ERDBNB', 'DOGEBNB', 'DUSKBNB', 'ANKRBNB', 'WINBNB', 'COSBNB', 'COCOSBNB', 'TOMOBNB', 'PERLBNB', 'CHZBNB', 'BANDBNB', 'BEAMBNB', 'XTZBNB', 'HBARBNB', 'NKNBNB', 'STXBNB', 'KAVABNB', 'ARPABNB', 'CTXCBNB', 'BCHBNB', 'TROYBNB', 'VITEBNB', 'FTTBNB', 'OGNBNB', 'DREPBNB', 'TCTBNB', 'WRXBNB', 'LTOBNB', 'STRATBNB', 'MBLBNB', 'COTIBNB', 'STPTBNB', 'SOLBNB', 'CTSIBNB', 'HIVEBNB', 'CHRBNB', 'MDTBNB', 'STMXBNB', 'IQBNB', 'DGBBNB', 'COMPBNB', 'SXPBNB', 'SNXBNB', 'VTHOBNB', 'IRISBNB', 'MKRBNB', 'DAIBNB', 'RUNEBNB', 'FIOBNB', 'AVABNB', 'BALBNB', 'YFIBNB', 'JSTBNB', 'SRMBNB', 'ANTBNB', 'CRVBNB', 'SANDBNB', 'OCEANBNB', 'NMRBNB', 'DOTBNB', 'LUNABNB', 'RSRBNB', 'PAXGBNB', 'WNXMBNB', 'TRBBNB', 'BZRXBNB', 'SUSHIBNB', 'YFIIBNB', 'KSMBNB', 'EGLDBNB', 'DIABNB', 'BELBNB', 'WINGBNB', 'SWRVBNB', 'CREAMBNB', 'UNIBNB', 'AVAXBNB', 'BAKEBNB', 'BURGERBNB', 'FLMBNB', 'CAKEBNB', 'SPARTABNB', 'XVSBNB', 'ALPHABNB', 'AAVEBNB', 'NEARBNB', 'FILBNB', 'INJBNB', 'CTKBNB', 'KP3RBNB', 'AXSBNB', 'HARDBNB', 'UNFIBNB', 'PROMBNB', 'BIFIBNB', 'ICPBNB', 'ARBNB', 'POLSBNB', 'MDXBNB']

    for coin_pair in binance_coin_pairs:

        trading_data = app.getHistoricalData(coin_pair, app.getGranularity())

        # analyse the market data
        trading_dataCopy = trading_data.copy()
        ta = TechnicalAnalysis(trading_dataCopy)
        ta.addAll()
        df = ta.getDataFrame()

        df_last = getInterval(df, app)

        if len(df_last.index.format()) > 0:
            current_df_index = str(df_last.index.format()[0])
        else:
            current_df_index = state.last_df_index

        if app.getSmartSwitch() == 1 and app.getGranularity() == 3600 and app.is1hEMA1226Bull() is True and app.is6hEMA1226Bull() is True:
            print('*** smart switch from granularity 3600 (1 hour) to 900 (15 min) ***')

            # telegram
            if not app.disableTelegram() and app.isTelegramEnabled():
                telegram = app.getChatClient()
                telegram.send(app.getMarket() + " smart switch from granularity 3600 (1 hour) to 900 (15 min)")

            app.setGranularity(900)
            list(map(s.cancel, s.queue))
            s.enter(5, 1, executeJob, (sc, app, state))

        if app.getSmartSwitch() == 1 and app.getGranularity() == 900 and app.is1hEMA1226Bull() is False and app.is6hEMA1226Bull() is False:

            app.setGranularity(3600)
            list(map(s.cancel, s.queue))
            s.enter(5, 1, executeJob, (sc, app, state))

        if app.getExchange() == 'binance' and app.getGranularity() == 86400:
            if len(df) < 250:
                # data frame should have 250 rows, if not retry
                print('error: data frame length is < 250 (' + str(len(df)) + ')')
                logging.error('error: data frame length is < 250 (' + str(len(df)) + ')')
                list(map(s.cancel, s.queue))
                s.enter(300, 1, executeJob, (sc, app, state))
        else:
            if len(df) < 300:
                if not app.isSimulation():
                    # data frame should have 300 rows, if not retry
                    print('error: data frame length is < 300 (' + str(len(df)) + ')')
                    logging.error('error: data frame length is < 300 (' + str(len(df)) + ')')
                    list(map(s.cancel, s.queue))
                    s.enter(300, 1, executeJob, (sc, app, state))

        if len(df_last) > 0:
            now = datetime.today().strftime('%Y-%m-%d %H:%M:%S')

            if not app.isSimulation():
                ticker = app.getTicker(app.getMarket())
                now = ticker[0]
                price = ticker[1]
                if price < df_last['low'].values[0] or price == 0:
                    price = float(df_last['close'].values[0])
            else:
                price = float(df_last['close'].values[0])

            if price < 0.0001:
                raise Exception(app.getMarket() + ' is unsuitable for trading, quote price is less than 0.0001!')

            # technical indicators
            ema12gtema26 = bool(df_last['ema12gtema26'].values[0])
            ema12gtema26co = bool(df_last['ema12gtema26co'].values[0])
            goldencross = bool(df_last['goldencross'].values[0])
            macdgtsignal = bool(df_last['macdgtsignal'].values[0])
            macdgtsignalco = bool(df_last['macdgtsignalco'].values[0])
            ema12ltema26 = bool(df_last['ema12ltema26'].values[0])
            ema12ltema26co = bool(df_last['ema12ltema26co'].values[0])
            macdltsignal = bool(df_last['macdltsignal'].values[0])
            macdltsignalco = bool(df_last['macdltsignalco'].values[0])
            obv = float(df_last['obv'].values[0])
            obv_pc = float(df_last['obv_pc'].values[0])
            elder_ray_buy = bool(df_last['eri_buy'].values[0])
            elder_ray_sell = bool(df_last['eri_sell'].values[0])

            # candlestick detection
            hammer = bool(df_last['hammer'].values[0])
            inverted_hammer = bool(df_last['inverted_hammer'].values[0])
            hanging_man = bool(df_last['hanging_man'].values[0])
            shooting_star = bool(df_last['shooting_star'].values[0])
            three_white_soldiers = bool(df_last['three_white_soldiers'].values[0])
            three_black_crows = bool(df_last['three_black_crows'].values[0])
            morning_star = bool(df_last['morning_star'].values[0])
            evening_star = bool(df_last['evening_star'].values[0])
            three_line_strike = bool(df_last['three_line_strike'].values[0])
            abandoned_baby = bool(df_last['abandoned_baby'].values[0])
            morning_doji_star = bool(df_last['morning_doji_star'].values[0])
            evening_doji_star = bool(df_last['evening_doji_star'].values[0])
            two_black_gapping = bool(df_last['two_black_gapping'].values[0])


            state.action = getAction(now, app, price, df, df_last, state.last_action, False)
            if state.action == "BUY":
                print(state.action)
            elif state.action == "SELL":
                print(state.action)
            else:
                print(state.action)


def main():
    try:
        # initialise logging
        logging.basicConfig(
            filename=app.getLogFile(),
            format='%(asctime)s - %(levelname)s: %(message)s',
            datefmt='%m/%d/%Y %I:%M:%S %p',
            filemode='a',
            level=logging.DEBUG,
            force=True
        )

        trading_data = app.startApp(account, state.last_action, banner=False)

        def runApp():
            # run the first job immediately after starting
            if app.isSimulation():
                executeJob(s, app, state, trading_data)
            else:
                executeJob(s, app, state)

            s.run()

        try:
            runApp()
        except KeyboardInterrupt:
            raise
        except:
            if app.autoRestart():
                # Wait 30 second and try to relaunch application
                time.sleep(30)
                print('Restarting application after exception...')

                # Cancel the events queue
                map(s.cancel, s.queue)

                # Restart the app
                runApp()
            else:
                raise

    # catches a keyboard break of app, exits gracefully
    except KeyboardInterrupt:
        print(datetime.now(), 'closed')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
    except(BaseException, Exception) as e:
        # catch all not managed exceptions and send a Telegram message if configured
        if not app.disableTelegram() and app.isTelegramEnabled():
            telegram = app.getChatClient()
            telegram.send('Bot for ' + app.getMarket() + ' got an exception: ' + repr(e))

        print(repr(e))

        raise


main()
