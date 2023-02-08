import pandas as  pd
from datetime import datetime
import numpy as np

def parse_dates(x):
    try:
        return datetime.strptime(x, "%Y-%m-%d")
    except:
        return None

def to_day_count(x, start_date):
    try:
        return x.toordinal()-start_date
    except:
        print(x)
        return -1

def day_count_to_date(x, start_date):
    return datetime.fromordinal(start_date + x)

def load_and_aggregate(fname, min_date="2021-01-01", bin_size=7, with_country=False):
    d = pd.read_csv(fname, sep='\t')
    d["datetime"] = d.date.apply(parse_dates)
    d = d.loc[d.datetime.apply(lambda x:x is not None)]
    start_date = datetime.strptime(min_date, "%Y-%m-%d").toordinal()

    d["day_count"] = d.datetime.apply(lambda x: to_day_count(x, start_date))
    d  = d.loc[d["day_count"]>=0]
    d["time_bin"] = d.day_count//bin_size

    if with_country:
        totals = d.groupby(by=["region", "country", "time_bin"]).count()["day_count"].to_dict()
        counts = d.groupby(by=["region", "country", "time_bin", "clade"]).count()["day_count"].to_dict()
    else:
        totals = d.groupby(by=["region", "time_bin"]).count()["day_count"].to_dict()
        counts = d.groupby(by=["region", "time_bin", "clade"]).count()["day_count"].to_dict()

    timebins = {x:day_count_to_date(x*bin_size, start_date) for x in d.time_bin.unique()}


    return d, totals, counts, timebins

def make_design_matrix(counts, totals, stiffness=7):
    geos = list(set([(x[0], x[1]) for x in totals.keys()]))
    regions = list(set([x[0] for x in totals.keys()]))
    timepoints = sorted(set([x[-1] for x in totals.keys()]))
    cats = sorted(set([x[-1] for x in counts.keys()]))

    from itertools import product

    region_params = {region_index: ri for ri, region_index in enumerate(product(regions, timepoints, cats))}
    n_region_params = len(region_params)
    #geo_params = {geo_index: gi+n_region_params for gi, geo_index in enumerate(product(geos, timepoints, cats))}

    # no countries for the time being
    # sum_i (n p_r(i) - k)^2/(pc + k(1-k/n)) + lam sum_(i>1) (p_r(i) - p_r(i-1))^2
    # the derivative with respect to p_r(j)
    # (n p_r(j) - k)/(pc + k(1-k/n)) + lam (2p_r(i) - p_r(i-1) - p_r(i+1)) = 0
    # n p_r(j)/(pc + k(1-k/n)) + lam (2p_r(i) - p_r(i-1) - p_r(i+1)) = k/(pc + k(1-k/n))

    matrix_contributions = []
    b = []
    pc = 3
    for cat, index in region_params.items():
        totals_index = tuple(cat[:-1])
        t = cat[1]
        first = t==timepoints[0]
        last = t==timepoints[-1]
        # diagonal
        res = 0
        b_val = 0
        if  totals_index in totals:
            n = totals[totals_index]
            k = counts.get(cat, 0)
            var = k*(1-k/n)+pc
            res += n/var
            b_val += k/var
        if not first:
            res += stiffness
        if not last:
            res += stiffness
        matrix_contributions.append((res, index, index))
        b.append(b_val)
        # off-diagonal t+1
        if not last:
            tp1_index = region_params[(cat[0], t+1, cat[-1])]
            matrix_contributions.append((-stiffness, index, tp1_index))
        # off-diagonal t-1
        if not first:
            tm1_index = region_params[(cat[0], t-1, cat[-1])]
            matrix_contributions.append((-stiffness, index, tm1_index))

    matrix_contributions_array = np.array(matrix_contributions)
    from scipy.sparse import csr_matrix
    from scipy.sparse.linalg import spsolve
    A = csr_matrix((matrix_contributions_array[:,0], (matrix_contributions_array[:,1], matrix_contributions_array[:,2])), shape=(n_region_params, n_region_params))
    sol = spsolve(A,b)

    freqs = pd.DataFrame([{'region':params[0], 'timepoint':params[1], 'cat':params[-1],'freq':sol[ri]} for params, ri in region_params.items()])
    return freqs

if __name__=='__main__':
    fname = "data/h3n2_clades.tsv"

    bin_size = 7
    data, totals, counts, time_bins = load_and_aggregate(fname, with_country=False, bin_size=7)
    freqs = make_design_matrix(counts, totals, stiffness = 20/bin_size)
    freqs["date"] = freqs.timepoint.apply(lambda x:time_bins[x])

    clades = freqs.cat.unique()

    region = 'europe'

    from matplotlib import pyplot as plt
    fig = plt.figure()
    for cat in clades:
        f = freqs.loc[(freqs.region==region)&(freqs.cat==cat)]
        if np.sum(f.freq)>0.1:
            plt.plot(f.date, f.freq, label=f'clade: {cat}')
    plt.legend(loc=2)
    fig.autofmt_xdate()
