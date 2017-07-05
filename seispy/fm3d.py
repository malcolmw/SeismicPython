from math import degrees,\
                 pi,\
                 radians
import seispy

def print_fm3d(vm, phase, propgrid, stretch=1.01, size_ratio=2, basement=30):
    return(print_propgrid(propgrid),
           print_vgrid(vm,
                       phase,
                       propgrid,
                       stretch=stretch,
                       size_ratio=2),
           print_interfaces(propgrid,
                            stretch=stretch,
                            size_ratio=size_ratio,
                            basement=basement))

def print_interfaces(propgrid, stretch=1.01, size_ratio=2, basement=30):
    igrid = _calculate_grid_parameters(propgrid)
    nlat, nlon = igrid["nlat"], igrid["nlon"]
    dlat, dlon = igrid["dlat"], igrid["dlon"]
    lat0, lon0 = igrid["lat0"], igrid["lon0"]
    blob = "2\n"\
           "{:d} {:d}\n"\
           "{:.4f} {:.4f}\n"\
           "{:.4f} {:.4f}\n".format(nlat, nlon,
                                    dlat, dlon,
                                    lat0, lon0)
    top = seispy.constants.EARTH_RADIUS + propgrid["h0"]
    bottom = seispy.constants.EARTH_RADIUS + propgrid["h0"] -\
            (propgrid["nr"] - 1) * propgrid["dr"]
    for r in (top, bottom):
        for ilat, ilon in [(ilat, ilon) for ilat in range(nlat)
                                        for ilon in range(nlon)]:
            blob += "{:.4f}\n".format(r)
    return(blob.rstrip())

def print_mode_set(file_mode=False,
                   no_pp_mode=False,
                   parallel_mode=False,
                   display_mode=False,
                   save_rays_mode=False,
                   save_timefields_mode=False):
    file_mode = "T" if file_mode is True else "F"
    no_pp_mode = "T" if no_pp_mode is True else "F"
    parallel_mode = "T" if parallel_mode is True else "F"
    display_mode = "T" if display_mode is True else "F"
    save_rays_mode = "T" if save_rays_mode is True else "F"
    save_timefields_mode = "T" if save_timefields_mode is True else "F"
    return("{}\tfile_mode\n"\
           "{}\tno_pp_mode\n"\
           "{}\tparallel_mode\n"\
           "{}\tdisplay_mode\n"\
           "{}\tsave_rays_mode\n"\
           "{}\tsave_timefields_modes".format(file_mode,
                                              no_pp_mode,
                                              parallel_mode,
                                              display_mode,
                                              save_rays_mode,
                                              save_timefields_mode))

def print_propgrid(grid):
    return("{:d} {:d} {:d}\n"\
           "{:.6f} {:.6f} {:.6f}\n"\
           "{:.6f} {:.6f} {:.6f}\n"\
           "5 10".format(grid["nr"], grid["nlat"], grid["nlon"],
                         grid["dr"], grid["dlat"], grid["dlon"],
                         grid["h0"], grid["lat0"], grid["lon0"] % 360))

def print_vgrid(vm, phase, propgrid, stretch=1.01, size_ratio=2):
    vgrid = _calculate_grid_parameters(propgrid)
    nr, nlat, nlon = vgrid["nr"], vgrid["nlat"], vgrid["nlon"]
    dr, dlat, dlon = vgrid["dr"], vgrid["dlat"], vgrid["dlon"]
    r0, lat0, lon0 = vgrid["r0"], vgrid["lat0"], vgrid["lon0"]
    blob = "1 1\n"\
           "{:d} {:d} {:d}\n"\
           "{:.4f} {:.4f} {:.4f}\n"\
           "{:.4f} {:.4f} {:.4f}\n".format(nr, nlat, nlon,
                                           dr, dlat, dlon,
                                           r0, lat0, lon0)
    for (ir, ilat, ilon) in [(ir, ilat, ilon) for ir in range(nr)\
                                                  for ilat in range(nlat)\
                                                  for ilon in range(nlon)]:
        lat = degrees(lat0 + dlat * ilat)
        lon = degrees(lon0 + dlon * ilon) % 360.
        r = r0 + dr * ir
        depth = seispy.constants.EARTH_RADIUS - r
        blob += "{:f}\n".format(vm(phase, lat, lon, depth))
    return(blob.rstrip())

def _calculate_grid_parameters(grid, stretch=1.01, size_ratio=2):
    pnr, pnlat, pnlon = grid["nr"], grid["nlat"], grid["nlon"]
    pdr, pdlat, pdlon = grid["dr"], radians(grid["dlat"]), radians(grid["dlon"])
    ph0, plat0, plon0 = grid["h0"], radians(grid["lat0"]), radians(grid["lon0"])
    plon0 %= 2 * pi
    pr0 = seispy.geometry.EARTH_RADIUS + ph0 - ((pnr - 1) * pdr)
    i = (pnr - 1) % size_ratio
    pnr = pnr + (size_ratio - i) if i > 0 else pnr
    i = (pnlat - 1) % size_ratio
    pnlat = pnlat + (size_ratio - i) if i > 0 else pnlat
    i = (pnlon - 1) % size_ratio
    pnlon = pnlon + (size_ratio - i) if i > 0 else pnlon
    nr = int((pnr - 1) / size_ratio) + 3
    nlat = int((pnlat - 1) / size_ratio) + 3
    nlon = int((pnlon - 1) / size_ratio) + 3
    dr = stretch * pdr * size_ratio
    dlat = stretch * pdlat * size_ratio
    dlon = stretch * pdlon * size_ratio
    r0 = pr0 - dr - (nr - 1) * dr * (stretch - 1.0) / 2
    lat0 = plat0 - dlat - (nlat - 1) * dlat * (stretch - 1.0) / 2
    lon0 = plon0 - dlon - (nlon - 1) * dlon * (stretch - 1.0) / 2
    return({"nr": nr, "nlat": nlat, "nlon": nlon,
            "dr": dr, "dlat": dlat, "dlon": dlon,
            "r0": r0, "lat0": lat0, "lon0": lon0})