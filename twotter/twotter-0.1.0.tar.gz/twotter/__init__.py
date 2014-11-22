from twotter.twotter import *
import sys

def main():
    tw = twotter.Twotter(sys.argv[1])
    tw.login()
    tw.get_pos()
    tw._close_session()
    tw.parse_json()
    tw.plot_aircraft()
    #plt.show() # or instead, tw.save_plot()
    tw.save_plot()

if __name__ == "__main__":
    main()
