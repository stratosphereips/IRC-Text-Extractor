import numpy as np
from sklearn.metrics import confusion_matrix


def compute_score(y_test, y_pred, verbose=True):
    conf = confusion_matrix(y_test, y_pred, labels=[0,1])
    TN, FP, FN, TP = conf.ravel()
    TPR = np.nan_to_num(round(TP / (TP + FN), 4))
    SPC = np.nan_to_num(round(TN / (FP + TN), 4))
    PPV = np.nan_to_num(round(TP / (TP + FP), 4))
    NPV = np.nan_to_num(round(TN / (TN + FN), 4))
    FPR = np.nan_to_num(round(FP / (FP + TN), 4))
    FDR = np.nan_to_num(round(FP / (FP + TP), 4))
    FNR = np.nan_to_num(round(FN / (FN + TP), 4))
    ACC = np.nan_to_num(round((TP + TN) / (TP + FP + TN + FN), 4))
    F1 = np.nan_to_num(round(2*TP / (2*TP + FP + FN), 4))
    
    if verbose:
        print('Confusion matrix:\n{}\n'.format(conf))
        print('Sensitivity(=Recall) TPR = TP / (TP + FN):\t\t{}'.format(round(TPR, 4)))
        print('Specificity SPC = TN / (FP + TN):\t\t\t{}'.format(round(SPC, 4)))
        print('Precision PPV = TP / (TP + FP):\t\t\t\t{}'.format(round(PPV, 4)))
        print('Negative Predictive Value NPV = TN / (TN + FN):\t\t{}'.format(round(NPV, 4)))
        print('False Positive Rate FPR = FP / (FP + TN)):\t\t{}'.format(round(FPR, 4)))
        print('False Discovery rate FDR = FP / (FP + TP):\t\t{}'.format(round(FDR, 4)))
        print('False Negative rate FNR = FN / (FN + TP):\t\t{}'.format(round(FNR, 4)))
        print('Accuraccy ACC = (TP + TN) / (P + N):\t\t\t{}'.format(round(ACC,4)))
        print('F1-score F1 = 2TP / (2TP + FP + FN):\t\t\t{}'.format(round(F1, 4)))
    
    return [TPR, SPC, PPV, NPV, FPR, FDR, FNR, ACC, F1]

# check Wikipedia: https://en.wikipedia.org/wiki/Moving_average
def simple_moving_average(x: [float], n: int) -> float:
    mean = np.zeros(len(x) - n + 1)
    tmp_sum = np.sum(x[0:n])
    for i in range(len(mean) - 1):
        mean[i] = tmp_sum
        tmp_sum -= x[i]
        tmp_sum += x[i + n]
    mean[len(mean) - 1] = tmp_sum
    return mean / n

# check Wikipedia: https://en.wikipedia.org/wiki/Moving_average
def exponential_moving_average(x: [float], alpha: float) -> float:
    mean = np.zeros(len(x))
    mean[0] = x[0]
    for i in range(1, len(x)):
        mean[i] = alpha * x[i] + (1.0 - alpha) * mean[i - 1]
    return mean