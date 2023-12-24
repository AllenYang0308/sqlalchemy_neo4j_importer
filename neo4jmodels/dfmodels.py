from abc import ABC, abstractmethod


class DataFrameCreator(ABC):

    @abstractmethod
    def create_data_frame(self, data):
        self.data = data
