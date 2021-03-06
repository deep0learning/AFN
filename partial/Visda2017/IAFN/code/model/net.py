import numpy as np
import torch
import torch.nn as nn
import torchvision
from torchvision import models
from torch.autograd import Variable
import torch.nn.functional as F
import math

"""
class ResBase(nn.Module):
    def __init__(self):
        super(ResBase, self).__init__()
        model_resnet50 = models.resnet50(pretrained=True)
        self.conv1 = model_resnet50.conv1
        self.bn1 = model_resnet50.bn1
        self.relu = model_resnet50.relu
        self.maxpool = model_resnet50.maxpool
        self.layer1 = model_resnet50.layer1
        self.layer2 = model_resnet50.layer2
        self.layer3 = model_resnet50.layer3
        self.layer4 = model_resnet50.layer4
        self.avgpool = model_resnet50.avgpool

    def forward(self, x):
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)
        x = self.maxpool(x)
        x = self.layer1(x)
        x = self.layer2(x)
        layer3 = self.layer3(x)
        x = self.layer4(layer3)
        x = self.avgpool(x)
        x = x.view(x.size(0), -1)
        #layer3 = layer3.view(layer3.size(0), -1)
        return layer3, x
"""

class ResBase50(nn.Module):
    def __init__(self):
        super(ResBase50, self).__init__()
        model_resnet50 = models.resnet50(pretrained=True)
        self.conv1 = model_resnet50.conv1
        self.bn1 = model_resnet50.bn1
        self.relu = model_resnet50.relu
        self.maxpool = model_resnet50.maxpool
        self.layer1 = model_resnet50.layer1
        self.layer2 = model_resnet50.layer2
        self.layer3 = model_resnet50.layer3
        self.layer4 = model_resnet50.layer4
        self.avgpool = model_resnet50.avgpool

    def forward(self, x):
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)
        x = self.maxpool(x)
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)
        x = self.avgpool(x)
        x = x.view(x.size(0), -1)
        return x


class DSNClassifier(nn.Module):
    def __init__(self, class_num=12, extract=True):
        super(DSNClassifier, self).__init__()
        self.avgpool = nn.AvgPool2d(14, stride=1)
        self.fc = nn.Linear(1024, class_num)
        self.extract = extract

    def forward(self, x):
        avg = self.avgpool(x)
        avg = avg.view(avg.size(0), -1)
        x = self.fc(avg)
        if self.extract:
            return avg, x
        return x


class ResClassifier(nn.Module):
    def __init__(self, class_num=12, extract=False):
        super(ResClassifier, self).__init__()
        self.fc1 = nn.Sequential(
            nn.Linear(2048, 1000),
            nn.BatchNorm1d(1000, affine=True),
            nn.ReLU(inplace=True),
            nn.Dropout()
            )
        self.fc2 = nn.Sequential(
            nn.Linear(1000, 1000),
            nn.BatchNorm1d(1000, affine=True),
            nn.ReLU(inplace=True),
            nn.Dropout()
            )
        self.fc3 = nn.Linear(1000, class_num)
        self.extract = extract

    def forward(self, x):
        fc1_emb = self.fc1(x)
        if self.training:
            fc1_emb.mul_(math.sqrt(0.5))
        fc2_emb = self.fc2(fc1_emb)
        if self.training:
            fc2_emb.mul_(math.sqrt(0.5))            
        logit = self.fc3(fc2_emb)

        if self.extract:
            return fc2_emb, logit
        return logit
