# implementation of the original statistical (veronika's) features (the 256px version, not 512)
# parts of the code more or less directly copied from the initial Veronika's jupyter ntb

import math
import numpy as np
import scipy.stats
import skimage.color
import findpeaks

import logging

logger = logging.getLogger("StatisticalFeatures logger")

class StatisticalFeatures:
	SECTORS_NUM = 24
	CIR_NUM = 32

	def __init__(self) -> None:

		# PRECOMPUTE CONSTANT CACHED ITEMS (IDENTICAL FOR ALL INPUTS)
		sz = 256 # expected size of the img on input to most functions (square SZxSZ, the cached masks etc are based on this value so the actual input must correspond); changing to 512 will NOT make the code equivalent to the 512 version
	
		# FT
		kfreq = np.fft.fftfreq(sz) * sz
		self._ft_knrm = np.sqrt(kfreq.reshape(-1,1)**2+kfreq.reshape(1,-1)**2).reshape(-1) # amplitudes of fourier vectors
		self._ft_kbins = np.linspace(.5, sz//2+.5, sz//2+1) # bins for the FT scpecturum histogram
		self._ft_kbins2 = np.pi * (self._ft_kbins[1:]**2 - self._ft_kbins[:-1]**2) # some multiplication factor for the PSD binning

		# pattern
		self._patt_mean_mask, self._patt_sum_all = self.precompute_sector_masks(sz) # the original "mean_mask" and "sum_all" variables from "mean_circular_sectors_cut" script

		# color
		self._clr_multicolored_bins = np.linspace(-128, 128, 129)

	def precompute_sector_masks(self, sz:int):
		# all the calls to "sector_mask" in "mean_circular_sectors_cut" (very slow in the original implementation) done once and cached
		# img assumed square sz x sz
		# do not change the default args, they ahve the same const values in other functions

		# Size of 1 sector in angles
		sector_size = int(360/self.SECTORS_NUM)
		START_NUM = 270

		# Find the middle of the image
		middle = (math.floor(sz/2), math.floor(sz/2))

		# result
		mean_mask = {}
		sum_all = np.zeros((self.CIR_NUM, math.ceil(self.SECTORS_NUM/2)))

		# Iterate through half of the sectors
		for i in range(math.ceil(self.SECTORS_NUM/2)):
			# Iterate through dividing circles
			for j in range(self.CIR_NUM):

				# Getting the big mask that the smaller will be subtracted from to create areas between two circles
				# The size of the circle is size of the image divided by the number of the circles
				if j != (self.CIR_NUM-1):
					big_size = math.floor(middle[0]/self.CIR_NUM)*(j+1)
				# The last circle is the whole image - circle is the size of the image
				else:
					big_size = middle[0]
				big_mask = self.sector_mask(sz, (middle[0], middle[1]), big_size, (START_NUM+i*sector_size, (START_NUM+sector_size)+i*sector_size))
				
				# Getting the small mask that will be subtracted from the bigger to create areas between two circles
				small_size = math.floor(middle[0]/self.CIR_NUM)*(j)
				small_mask = self.sector_mask(sz, (middle[0], middle[1]), small_size, (START_NUM+i*sector_size, (START_NUM+sector_size)+i*sector_size))
				
				# result
				mm = big_mask & (~small_mask)
				mean_mask[(i,j)] = mm
				sum_all[j,i] = np.count_nonzero(mm)

		return mean_mask, sum_all # Used in "mean_circular_sectors_cut" as: mean_mask = _mean_mask[(i,j)] etc, sum_all is just like 'sum_all' from the original code, just computed once


	def sector_mask(self, sz,centre,radius,angle_range):
		# function from https://stackoverflow.com/questions/18352973/mask-a-circular-sector-in-a-numpy-array
		# sz - shape of the original image to mask (SZ x SZ)
		# centre - tuple of centre coordinates of the circle to mask (middle of the image)
		# radius - size of the circle to mask
		# angle_range - tuple of range of the circle
		# returns mask of the specified parameters
		x,y = np.ogrid[:sz,:sz]
		cx,cy = centre
		tmin,tmax = np.deg2rad(angle_range)
		# ensure stop angle > start angle
		if tmax < tmin:
				tmax += 2*np.pi
		# convert cartesian --> polar coordinates
		r2 = (x-cx)*(x-cx) + (y-cy)*(y-cy)
		theta = np.arctan2(x-cx,y-cy) - tmin
		# wrap angles between 0 and 2*pi
		theta %= (2*np.pi)
		# circular mask
		circmask = r2 <= radius*radius
		# angular mask
		anglemask = theta <= (tmax-tmin)
		return circmask*anglemask

	def rgb2other(self, img):
		# conversion to the LCH space that the features operate in
		
		# Converting RGB to Lab image
		img_lab = skimage.color.rgb2lab(img, "D65")
		img_lch = skimage.color.lab2lch(img_lab)
		return img_lab, img_lch

	def center_crop(self, img:np.ndarray, sz:int)->np.ndarray:
		# square center crop (should be compatible with the original veronika's jupyter)
		# crashes when img.size < sz
		if(img.shape[0] < sz or img.shape[1] < sz): raise ValueError(f"img of size {img.shape[:2]} too small for crop to {sz}")

		pad = math.floor((img.shape[0]-sz)/2), math.floor((img.shape[1]-sz)/2)
		return img[pad[0]:pad[0]+sz, pad[1]:pad[1]+sz]

	def simple_features(self, img:np.ndarray)->tuple[float]:
		# img - just 1 channel HW (luminance)
		# percentiles
		min_val, max_val = np.percentile(img, (1,99))
		# mean, var
		mean_val = np.mean(img)
		val0 = img-mean_val
		var_val = np.mean(val0**2)
		if(var_val > 0):
			skew_val = np.mean(val0**3)/var_val**(3/2)
			kurt_val = np.mean(val0**4)/var_val**2 - 3
		else:
			skew_val = 0
			kurt_val = 0
		return max_val, min_val, mean_val, var_val, skew_val, kurt_val

	### FT features

	def count_only_psd(self, ft_ps:np.ndarray):
		# NOTE: requires already precomputed fft2 power spectrum on input: abs(fft2(img))**2
		# Binning the values of amplitudes
		Abins, _, _ = scipy.stats.binned_statistic(self._ft_knrm,  ft_ps.reshape(-1), statistic="mean", bins=self._ft_kbins)
		return Abins*self._ft_kbins2

	def count_freq(self, ft_ps, borders = (0, 5, 50, 128)):
		# ft_ps: already precomputed fft2 power spectrum of the img: abs(fft2(img))**2
		# borders - list of borders between which the mean of the frequency will be computed
		# returns a list of means of amplitudes of frequencies between borders
		mean_all = []
		# Getting the PSD
		Abins = self.count_only_psd(ft_ps)
		# Iterating through the area set by borders
		for i in range(len(borders)-1):
			# Calculating the mean of the amplitudes between borders
			mean_all.append(np.mean(Abins[borders[i]:borders[i+1]]))
		return mean_all

	### pattern features

	def count_directionality_cut(self, all_sum):
		# Number of columns - of sections
		n = all_sum.shape[0]
		# Select the maximum column values
		max_col = np.max(all_sum)
		# Count the directionality
		direct = np.sum(max_col - all_sum)/(n * max_col)

		return direct

	def count_pattern_str(self, means):
		# Compute mean of columns - info about the whole sector of Fourier from center to edge - through all frequencies
		# Find the maximum
		maxim = np.argmax(means)
		ratio = []
		for i in range(len(means)):
			if i != maxim:
				# Compute the ratio between the sector and the max value sector
				ratio.append(means[maxim]/means[i])
		# Mean of the ratios - how on average is the value different from the max
		return np.mean(ratio)

	def mean_circular_sectors_cut(self, ft_ps):
		# NOTE: ft_ps: already precomputed fft2 power spectrum of the img: abs(fft2(img))**2
		# requires pre-computed masks by precompute_sector_masks

		# Setting up the containers, only half of the image is used - sectors are divided by 2
		mean_all = np.zeros((self.CIR_NUM, math.ceil(self.SECTORS_NUM/2)))
		
		# Prepare the image for Fourier transform
		fourier = np.fft.fftshift(ft_ps)

		# Iterate through half of the sectors
		for i in range(math.ceil(self.SECTORS_NUM/2)):
			# Iterate through dividing circles
			for j in range(self.CIR_NUM):
				mean_mask = self._patt_mean_mask[(i,j)]
				mean_all[j,i] = np.mean(fourier[mean_mask])
				
		return mean_all*self._patt_sum_all


	def count_pattern(self, ft_ps):
		# NOTE: (ft_ps): requries precomputed fft2 power spectrum of the img: abs(fft2(img))**2
		# +also requires pre-computed sector masks

		means_mult = self.mean_circular_sectors_cut(ft_ps)

		# Compute sum of columns - info about the whole sector of Fourier from center to edge - through all frequencies
		all_sum = np.sum(means_mult, axis=0)

		# JK: for some (nearly constant) imgs all these features are non-informative and result in nans, skip if this is going to be the case
		if(not np.any(all_sum)):
			direct = 0
			patt_str = 1
			len_peaks = 1 # this is what findpeaks returns for constant vectors
			return direct, patt_str, len_peaks
		
		# Directionality computation
		direct = self.count_directionality_cut(all_sum)
		
		# Pattern stregth computation
		patt_str = self.count_pattern_str(all_sum)
		
		# Pattern number computation
		
		# Scaling to (0,1) - just need information about peaks not their size
		min_ = np.min(all_sum, axis=0); max_ = np.max(all_sum, axis=0)
		all_sum_red = (all_sum - min_) / (max_ - min_) # sklearn...minmax_scale

		# Find peaks
		fp = findpeaks.findpeaks(method="topology", verbose=0)
		local_max = fp.fit(all_sum_red)
		# Peaks values
		peaks = local_max["persistence"][["y", "score"]].values

		# Select only the important peaks - higher score than 0.5
		peaks_new = [i[0] for i in peaks if i[1] > 0.5]

		# If both peaks at the ends are found, the end one is deleted - ensures the "circle" nature, connect them into one peak
		if 0 in peaks_new and 11 in peaks_new:
			len_peaks = len(peaks_new) - 1 # ignore the 11 (wrap-around of the same peak)
		else:
			len_peaks = len(peaks_new)
			
		return direct, patt_str, len_peaks

	### color related features

	def color_features(self, img_lab, img_lch):
		# NOTE: the two color features merged into one function (originally "count_multicolored" and one liner in the main script)

		# Mean chroma - weighted by luminance
		mean_chr_int = np.mean((img_lch[..., 0]*img_lch[..., 1]))

		# 1 - A color channel
		# 2 - B color channel
		src_X = img_lab[...,1].reshape(-1)
		src_Y = img_lab[...,2].reshape(-1)
		
		# Calculating color space data as a 2D histogram
		Z, _, _ = np.histogram2d(src_X, src_Y, bins=[self._clr_multicolored_bins, self._clr_multicolored_bins], weights=img_lab[...,0].reshape(-1))
		
		# Finding peaks in the 2D histogram
		# Important parameter "limit", to limit the score of peaks - suppresses noise
		fp = findpeaks.findpeaks(limit=30, verbose=0)
		local_max = fp.fit(Z)
		
		# Return number of peaks for image
		multicol = len(local_max["persistence"][["x", "y"]].values) - 1 # JK: for some reason, I keep getting +1 values wrt to the original veronika's script...? (also, findpeaks is nondeterministic so the values can fluctuate)

		return mean_chr_int, multicol


	### ALL FEATURES

	def compute(self, img:np.ndarray)->np.ndarray:
		# returns feature vector of the 14 JF features, should be in the same order as in the orig script
		# img: rgb

		logger.debug("Precomputing common stuff")
		# precompute common stuff
		img_lab, img_lch = self.rgb2other(img)
		crop_sz = 256
		if(img_lch.shape[:2] != (crop_sz, crop_sz)):
			img_crop = self.center_crop(img_lch[...,0], crop_sz) # pre-cropped luma channel
		else:
			img_crop = img_lch[...,0]
		ft_ps = np.fft.fft2(img_crop)
		ft_ps = np.abs(np.conj(ft_ps)*ft_ps) # FT power spectrum

		logger.debug("Computing rest of the features")
		# features
		simple = self.simple_features(img_lch[...,0]) # as per orig script, calculated from full-size img if available
		ft = self.count_freq(ft_ps)
		pattern = self.count_pattern(ft_ps)
		clr = self.color_features(img_lab, img_lch)

		logger.debug("Returning stats results")
		return np.array((*simple, pattern[0], *ft, clr[0], *pattern[1:], clr[1]))

	
