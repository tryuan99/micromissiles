import matplotlib.pyplot as plt
import numpy as np
from absl import app, flags

import utils.visualization.mpl_config
from utils.network.sparam_viewer import SParamViewer

FLAGS = flags.FLAGS


def main(argv):
    assert len(argv) == 1

    s2p_viewer = SParamViewer(FLAGS.file)
    f = s2p_viewer.frequency()
    for i in (1, 2):
        for j in (1, 2):
            sp = s2p_viewer.s(i, j)
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 6), sharex=True)
            ax1.semilogx(f, 20 * np.log10(np.abs(sp)))
            ax2.semilogx(f, np.rad2deg(np.angle(sp)))
            ax2.set_xlabel("Frequency [Hz]")
            ax1.set_ylabel("Magnitude [dB]")
            ax2.set_ylabel("Phase [deg]")
            plt.suptitle(f"S{i}{j}")
            plt.show()


if __name__ == "__main__":
    flags.DEFINE_string("file", None, "Touchstone file.")
    flags.mark_flag_as_required("file")

    app.run(main)
