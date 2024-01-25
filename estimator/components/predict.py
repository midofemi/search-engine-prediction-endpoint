import os
from from_root import from_root
from estimator.components.custom_ann import CustomAnnoy
from estimator.components.storage_helper import StorageConnection
from estimator.entity.config import PredictConfig
from estimator.components.model import NeuralNet
from torchvision import transforms
from PIL import Image
from torch import nn
import numpy as np
import torch
import io


class Prediction(object):
    """
    Prediction class Prepares the model endpoint
    """
    def __init__(self):
        self.config = PredictConfig()
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.initial_setup()

        self.ann = CustomAnnoy(self.config.EMBEDDINGS_LENGTH,
                               self.config.SEARCH_MATRIX)

        self.ann.load(self.config.MODEL_PATHS[0][0])
        self.estimator = self.load_model()
        self.estimator.eval()
        self.transforms = self.transformations()

    @staticmethod
    def initial_setup():
        """
        Create the connections to AWS and get both CNN and ANN models from AWS
        """
        if not os.path.exists(os.path.join(from_root(), "artifacts")):
            os.makedirs(os.path.join(from_root(), "artifacts"))
        connection = StorageConnection()
        connection.get_package_from_testing()

    def load_model(self):
        """
        Load the model but don't add the last layer
        """
        model = NeuralNet()
        model.load_state_dict(torch.load(self.config.MODEL_PATHS[1][0], map_location=self.device))
        return nn.Sequential(*list(model.children())[:-1])

    def transformations(self):
        """
        We talked about this before. Whenever we get an input image from users, we need to apply transformation on that image
        """
        TRANSFORM_IMG = transforms.Compose(
            [transforms.Resize(self.config.IMAGE_SIZE),
             transforms.CenterCrop(self.config.IMAGE_SIZE),
             transforms.ToTensor(),
             transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                  std=[0.229, 0.224, 0.225])]
        )

        return TRANSFORM_IMG

    def generate_embeddings(self, image):
        """
        Pass that input image to our CNN model and generate embeddings for that image
        """
        image = self.estimator(image.to(self.device))
        image = image.detach().cpu().numpy()
        return image

    def generate_links(self, embedding):
        """
        Do the same for our ANN model. Meaning pass those embedding we have generated above to our ANN model and send us the links based on
        our search
        """
        return self.ann.get_nns_by_vector(embedding, self.config.NUMBER_OF_PREDICTIONS)

    def run_predictions(self, image):
        """
        Send our links from above as an output
        """
        image = Image.open(io.BytesIO(image))
        if len(image.getbands()) < 3:
            image = image.convert('RGB')
        image = torch.from_numpy(np.array(self.transforms(image)))
        image = image.reshape(1, 3, 256, 256)
        embedding = self.generate_embeddings(image)
        return self.generate_links(embedding[0])
