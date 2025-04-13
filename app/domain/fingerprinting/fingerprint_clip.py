# code for JF, calcs fingerprint from two frames usign clip and pretrained model

import numpy as np
import torch, torch.nn as nn
import imageio.v3 as imageio
import PIL.Image

# mlp class
class MLP(nn.Module):
	def __init__(self, layers:tuple[int]) -> None:
		super().__init__()

		# modules
		self.layers = nn.Sequential()
		for i, (n_in, n_out) in enumerate(zip(layers[:-1], layers[1:])):
			self.layers.append(nn.Linear(n_in, n_out))
			if(i < len(layers)-2): # no activation in the final layer
				self.layers.append(nn.GELU())

	def forward(self, x:torch.Tensor)->torch.Tensor:
		return self.layers(x)

# clip preprocess
def clip_preprocess(img:np.ndarray, sz_resize:int, sz_crop:int=224)->torch.Tensor:
	# functions that simulate 'preprocess' from clip (with appropriate args is exactly equivalent) but acts on np images
	# sz_resize: smaller edge (h,w) will be this big
	# sz_crop: center crop to square target size; should be equivalent with torchvision center_crop
		
	# resize

	#print(type(img))

	if(sz_resize):
		min_sz = min(img.shape[:2])
		sz = (int(img.shape[0]/min_sz*sz_resize), int(img.shape[1]/min_sz*sz_resize))
		img = np.array(PIL.Image.fromarray(img).resize(size=(sz[1], sz[0]), resample=PIL.Image.Resampling.BICUBIC)) # in clip preprocess they use BICUBIC

	# center crop
	crop_top = int(round((img.shape[0] - sz_crop) / 2.0))
	crop_left = int(round((img.shape[1] - sz_crop) / 2.0))
	img = img[crop_top:(crop_top+sz_crop), crop_left:(crop_left+sz_crop)]

	# to tensor
	img = torch.from_numpy(img.transpose(2,0,1).astype(np.float32)/255) # HWC -> CHW; to [0,1]

	# normalize
	mean = torch.as_tensor((0.48145466, 0.4578275, 0.40821073), dtype=torch.float32).view(-1,1,1)
	std = torch.as_tensor((0.26862954, 0.26130258, 0.27577711), dtype=torch.float32).view(-1,1,1)
	return img.sub_(mean).div_(std)



