## scale up the weights
def scaling_weight(weight, scalar):
    print("[INFO] scaling weight")

    weight_list=[]
    for i in range(len(weight)):
        # print(weight[i].scale())
        weight_list.append(scalar * weight[i])
    return weight_list

## aggregated the weights
def aggregation_parameter(weight, gm_weights, alpha):
    print("[INFO] Aggregating single client update!")
    avg_weight = []
    for gob, loc in zip(gm_weights, weight):
        ## Standard FedAvg formula: q_new = (1-alpha) * global + alpha * local
        w1 = (1 - alpha) * gob
        w2 = alpha * loc
        avg = w1 + w2
        avg_weight.append(avg)
    return avg_weight

#--------------------------------------------------------------------------------
