import torch.nn as nn
from models.team17_fden import block as B
import torch

def make_model(args, parent=False):
    model = FDEN()
    return model


class FDEN(nn.Module):
    def __init__(self, in_nc=3, nf=29, num_modules=4, out_nc=3, upscale=4):
        super(FDEN, self).__init__()

        self.fea_conv = B.conv_layer(in_nc, nf, kernel_size=3)

        # IMDBs
        self.IMDB1 = B.FDEB(in_channels=nf)
        self.IMDB2 = B.FDEB(in_channels=nf)
        self.IMDB3 = B.FDEB(in_channels=nf)
        self.IMDB4 = B.FDEB(in_channels=nf)
        self.c = B.conv_block(nf * num_modules, nf, kernel_size=1, act_type='lrelu')

        self.LR_conv = B.conv_layer(nf, nf, kernel_size=3)

        upsample_block = B.pixelshuffle_block
        self.upsampler = upsample_block(nf, out_nc, upscale_factor=4)
        self.scale_idx = 0


    def forward(self, input):
        out_fea = self.fea_conv(input)
        out_B1 = self.IMDB1(out_fea)
        out_B2 = self.IMDB2(out_B1)
        out_B3 = self.IMDB3(out_B2)
        out_B4 = self.IMDB4(out_B3)

        out_B = self.c(torch.cat([out_B1, out_B2, out_B3, out_B4], dim=1))
        out_lr = self.LR_conv(out_B) + out_fea

        output = self.upsampler(out_lr)

        return output

    def set_scale(self, scale_idx):
        self.scale_idx = scale_idx
