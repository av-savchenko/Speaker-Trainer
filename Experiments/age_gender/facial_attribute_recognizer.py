import onnxruntime as ort
import numpy as np
import cv2

ethnicity_descriptions=['','White', 'Black', 'Asian', 'Indian', 'Latino or Middle Eastern']
class FacialAttributeRecognizer:
    #supported values of model_name: age_gender_ethnicity_lagenda_mbf_ft, age_gender_ethnicity_lagenda_enet0_ft
    def __init__(self, model_name='age_gender_ethnicity_lagenda_mbf_ft'):
        if 'mbf' in model_name:
            self.mean=[0.5, 0.5, 0.5]
            self.std=[0.5, 0.5, 0.5]
            self.img_size=112
        else:
            self.mean=[0.485, 0.456, 0.406]
            self.std=[0.229, 0.224, 0.225]
            self.img_size=224
        self.num_classes=96
        self.ort_session = ort.InferenceSession('models/'+model_name+'.onnx',providers=['CPUExecutionProvider'])
    
    def preprocess(self,img):
        x=cv2.resize(img,(self.img_size,self.img_size))/255
        for i in range(3):
            x[..., i] = (x[..., i]-self.mean[i])/self.std[i]
        return x.transpose(2, 0, 1).astype("float32")[np.newaxis,...]

    @staticmethod
    def expected_age(age_probabs):        
        indices=age_probabs.argsort()[::-1]#[:2]
        norm_preds=age_probabs[indices]/np.sum(age_probabs[indices])

        res_age=0
        for age,probab in zip(indices,norm_preds):
            res_age+=age*probab
        return res_age
    
    @staticmethod
    def get_ethnicity(ethnicity_preds):
        if ethnicity_preds is not None:
            ethnicity_ind=np.argmax(ethnicity_preds)+1
        else:
            ethnicity_ind=0
        return ethnicity_descriptions[ethnicity_ind]
    
    def get_attribute_probabs(self,face_img):
        scores=self.ort_session.run(None,{"input": self.preprocess(face_img)})[0][0]
        #print(scores)
        age_probabs=np.exp(scores[:self.num_classes])
        age_probabs=age_probabs/age_probabs.sum()

        gender_probabs=np.exp(scores[self.num_classes:self.num_classes+2])
        gender_probabs=gender_probabs/gender_probabs.sum()
        #isMale=gender_probabs[0]>gender_probabs[1]
        
        ethnicity_probabs=None
        if len(scores)>self.num_classes+2:
            ethnicity_probabs=np.exp(scores[self.num_classes+2:])
            ethnicity_probabs=ethnicity_probabs/ethnicity_probabs.sum()
        return age_probabs,gender_probabs[0],ethnicity_probabs

    def predict_attributes(self,face_img, estimage_age=False):
        age_probabs,male_probab,ethnicity_probabs=self.get_attribute_probabs(face_img)
        if estimage_age:
            age_pred=self.expected_age(age_probabs)
        else:
            age_pred=age_probabs.argmax()
        return age_pred,male_probab>0.5,self.get_ethnicity(ethnicity_probabs)
    
    