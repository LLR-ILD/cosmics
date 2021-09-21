import logging

import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import least_squares, minimize
from scipy.stats import norm


def check_fit_result(fit_result):
    if not fit_result.success:
        logger = logging.getLogger(__name__)
        logger.warning(f"Invalid fit result!\n{fit_result}.")


class SumEnergyFit:
    def __init__(self, events, n_bins=25):
        self.e_sum = events.sum_energy
        self._n_bins = n_bins

        axs = self._prepare_plotting()
        self.plot_remove_zero(axs[0])
        self.plot_identify_noise_through_negative(axs[1])
        self.plot_double_gaussian(axs[2])
        self.fig.tight_layout()

    def _prepare_plotting(self):
        self.fig, self.axs = plt.subplots(figsize=(12, 4), ncols=3)
        self.fig.suptitle("sum_energy")
        self._bin_edges = np.linspace(
            min(self.e_sum), max(self.e_sum), self._n_bins + 1
        )
        self._bin_width = self._bin_edges[1] - self._bin_edges[0]
        self._bin_centers = (self._bin_edges[1:] + self._bin_edges[:-1]) / 2
        self._x_cont = np.linspace(self._bin_edges[0], self._bin_edges[-1], 10_000)
        self._fit_results = []
        return self.axs

    def plot_remove_zero(self, ax):
        ax.set_title("Remove the zero-energy events")
        ax.hist(self.e_sum, bins=self._bin_edges, label="all", color="C1")
        self._counts, _, _ = ax.hist(
            self.e_sum[self.e_sum != 0], bins=self._bin_edges, label="!= 0", color="C0"
        )
        ax.legend()

    def plot_identify_noise_through_negative(self, ax):
        ax.set_title("Identify noise through negative-region")
        x = self.e_sum[self.e_sum != 0]
        x_neg = x[x < 0]
        bc = self._bin_centers
        bw = self._bin_width

        # Noise fit.
        def lh_noise_gaussian(p):
            loc, scale = 0, p[0]
            return len(x_neg) * np.log(scale) + sum((x_neg - loc) ** 2) / scale ** 2 / 2

        init_noise = (5000,)
        res = minimize(lh_noise_gaussian, init_noise)
        self._fit_results.append(res)
        print(res)
        check_fit_result(res)
        noise_label = fr"noise fit: $\mathcal{{N}}(0, {res.x[0]:.1f})$ ($\mu$ fixed)"

        norm_f = 2 * len(x_neg) * bw
        y = norm_f * norm.pdf(self._x_cont, scale=res.x[0])

        ax_inset = ax.inset_axes([0.12, 0.25, 0.35, 0.35])
        ax_inset.patch.set_alpha(0.5)
        ax_inset.hist(x_neg, bins=self._bin_edges, color="C0")
        ax_inset.plot(self._x_cont, y, color="C3")
        ax.plot(self._x_cont, y, color="C3", label=noise_label)

        noise_norm = (2 * len(x_neg)) * bw
        noise_counts = noise_norm * norm.pdf(self._bin_centers, scale=res.x[0])
        all_counts, _ = np.histogram(np.array(x), bins=self._bin_edges)
        signal_counts = all_counts - noise_counts
        ax.bar(
            bc,
            noise_counts,
            bw,
            bottom=signal_counts,
            color="C1",
            label="noise estimate per bin",
        )
        ax.bar(
            bc,
            signal_counts,
            bw,
            color="C0",
            hatch="//",
            edgecolor="k",
            fill=False,
            label="excess signal",
        )

        # Signal fit on top of noise.
        # This has to be done in a binned procedure (-> least squares).
        norm_s = sum(signal_counts) * bw

        def lsq_signal_gaussian(p, x, y):
            return y - norm_s * norm.pdf(x, loc=p[0], scale=p[1])

        init_signal = (bc[np.argmax(signal_counts)], init_noise[0])
        res_signal = least_squares(
            lsq_signal_gaussian, init_signal, args=(bc, signal_counts)
        )
        self._fit_results.append(res_signal)
        check_fit_result(res_signal)
        signal_label = fr"signal fit: $\mathcal{{N}}({res_signal.x[0]:.1f}, {res_signal.x[1]:.1f})$"

        y = norm_s * norm.pdf(self._x_cont, loc=res_signal.x[0], scale=res_signal.x[1])
        ax.plot(self._x_cont, y, ls="--", lw=2, color="k", label=signal_label)
        ax.set_ylim((None, 1.7 * max(all_counts)))  # Some empty space for legend.
        ax.legend()

    def plot_double_gaussian(self, ax):
        ax.set_title("Direct double-gaussian fit")
        x = self.e_sum[self.e_sum != 0]
        bw = self._bin_width

        def double_gauss(x, p):
            g_noise = norm.pdf(x, loc=p[1], scale=p[2])
            g_signal = norm.pdf(x, loc=p[3], scale=p[4])
            pdf = p[0] * g_noise + (1 - p[0]) * g_signal
            return pdf

        def lh(p):
            return -sum(np.log(double_gauss(x, p))) / len(x)

        init_p_noise = 2 * sum(x < 0) / len(x)
        s = 4000
        init = (init_p_noise, 0, s, 3 * s, 0.5 * s)
        bounds = [(0, 1)] + [(-2000, 2000)] + 3 * [[0, 20_000]]
        bounds = None
        res = minimize(lh, init, bounds=bounds, method="Nelder-Mead")

        n = len(x) * bw
        y1 = n * res.x[0] * norm.pdf(self._x_cont, loc=res.x[1], scale=res.x[2])
        y2 = n * (1 - res.x[0]) * norm.pdf(self._x_cont, loc=res.x[3], scale=res.x[4])
        y = y1 + y2
        ax.hist(x, self._bin_edges, color="C1")
        l0 = fr"double Gaussian ({100 * res.x[0]:.1f}% $\mathcal{{N}}_1$)"
        l1 = fr"$\mathcal{{N}}_1({res.x[1]:.1f}, {res.x[2]:.1f})$"
        l2 = fr"$\mathcal{{N}}_2({res.x[3]:.1f}, {res.x[4]:.1f})$"
        ax.plot(self._x_cont, y, color="C0", label=l0)
        ax.plot(self._x_cont, y1, ls="--", color="C3", label=l1)
        ax.plot(self._x_cont, y2, ls="--", color="k", label=l2)
        ax.legend(title="Rather unstable,\ndepends on initial values")
