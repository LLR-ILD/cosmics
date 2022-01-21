def savefig(fig, name, **kw):
    fig_kws = dict(facecolor="white", dpi=300)
    fig_kws.update(**kw)
    fig.tight_layout()
    fig.savefig(name, **fig_kws)
