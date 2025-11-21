import joblib
import os

model = None

def load_model():
    base_path = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(base_path, "model_v1.pkl")
    
    print(f"Carregando modelo de IA: {model_path}")
    try:
        model = joblib.load(model_path)
        print("Modelo carregado com sucesso!")
    except Exception as e:
        print(f"Erro ao carregar o modelo: {e}")
        
def predict_viabilidade(dados_entrada):
    if model is None:
        load_model()
    
    if model:
        return model.predict([dados_entrada])[0]
    
    return 0.0