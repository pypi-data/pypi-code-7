from statistics import mean, pstdev
import math

from dynamicForms.statistics.serializers import NumericStatisticsSerializer 

class NumericStatistics():
    """
    Class with the statistics info of a number  field  
    """
    
    def __init__(self, data_list):
        # Null values are counted as 0
        listTotal = []
        # Without null values
        list = []
        self.total_filled = 0
        self.total_not_filled = 0
        self.quintilesX  = []
        self.quintilesY = []
        
        for data in data_list:
            if data != "":
                listTotal.append(int(data))
                list.append(int(data))
                self.total_filled += 1 
            else:
                listTotal.append(0)
                self.total_not_filled += 1 

        if list != []:  
            self.mean = round(mean(list), 2)
            self.standard_deviation = round(pstdev(list, self.mean), 2)
            minimum  = min(list)
            maximum  = max(list)

            quintile_length  = math.floor((maximum - minimum + 1) /5)
            # First 4 quintiles
            first = minimum
            for i in range(1, 5):
                second = first + quintile_length
                quintileX = "[" + str(first) + ", " + str(second) + ")" 
                self.quintilesX.append(quintileX)
                quintileY = 0
                for num in list:
                    if (first <= num) and (num < second):
                        quintileY += 1
                self.quintilesY.append(quintileY)
                first = second
            # Last quintile
            self.quintilesX.append("[" + str(first) + ", " + str(maximum) + "]")
            quintileY = 0
            for num in list:
                if (first <= num) and (num <= maximum):
                    quintileY += 1
            self.quintilesY.append(quintileY)
        else:
            self.mean = 0
            self.standard_deviation = 0
        self.total_mean = round(mean(listTotal), 2)
        self.total_standard_deviation = round(pstdev(listTotal, self.total_mean), 2)
       
            

    def getSerializedData(self):
        return NumericStatisticsSerializer(self).data
