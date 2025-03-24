import React, { useState, useEffect } from 'react';
import { ArrowLeftCircle, CheckCircle2, Sliders, Brain, Play,Pause, Lock, RefreshCw } from 'lucide-react';
import './toogle.css';
import './loader.css';


interface CalibrationStep {
  id: number;
  movement: string;
  description: string;
  completed: boolean;
}

const calibrationSteps: CalibrationStep[] = [
  { id: 0, movement: "Mano Abierta", description: "Mantén la mano completamente abierta", completed: false },
  { id: 1, movement: "Mano Cerrada", description: "Cierra el puño completamente", completed: false },
  { id: 2, movement: "Punzada Fina", description: "Realiza un agarre de precisión", completed: false },
  { id: 3, movement: "Punzada Gruesa", description: "Realiza un agarre fuerte", completed: false },
  { id: 4, movement: "Mano Adentro", description: "Dobla tu muñeca hacia tu antebrazo", completed: false },
  { id: 5, movement: "Mano Afuera", description: "Dobla tu muñeca hacia la parte exterior del brazo", completed: false }
];

interface ProgressState {
  calibrationCompleted: boolean;
  trainingCompleted: boolean;
  modelReady: boolean;
}


const fetchAccuracy = async () => {
  try {
    const response = await fetch('http://localhost:5000/api/get-accuracy', {
      method: 'POST',
    });

    if (response.ok) {
      const data = await response.json();
      return data.accuracy; // ← valor recibido
    } else {
      console.error('Error al obtener accuracy');
      return null;
    }
  } catch (error) {
    console.error('Error en la petición:', error);
    return null;
  }
};


function App() {
  const [currentSection, setCurrentSection] = useState<'menu' | 'calibration' | 'training' | 'execution'>('menu');
  const [currentStep, setCurrentStep] = useState(0);
  const [isCollecting, setIsCollecting] = useState(false);
  const [isTraining, setIsTraining] = useState(false);
  const [accuracy, setAccuracy] = useState<number | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [isConnected, setIsConnected] = useState<boolean | null>(null);
  const [progress, setProgress] = useState<ProgressState>({
    
    calibrationCompleted: false,
    trainingCompleted: false,
    modelReady: false
  });

  useEffect(() => {
    fetch('http://localhost:5000/api/check')
        .then(res => res.json())
        .then(data => {
            setProgress(prev => ({
                ...prev,
                calibrationCompleted: data["MyoDataset.csv"],
                trainingCompleted: data["modelo_LSTM.keras"],
                modelReady: data["modelo_LSTM.keras"],
            }));
        })
        .catch(error => {
            console.error("Error fetching:", error);
        });
}, []);

useEffect(() => {
  if (currentSection === 'training') {
    const getAccuracy = async () => {
      const acc = await fetchAccuracy();
      if (acc !== null) setAccuracy(acc);
    };
    getAccuracy();
  }
}, [currentSection]);

  
  const startCalibration = async () => {
    try {
      setIsCollecting(true);
      const response = await fetch('http://localhost:5000/api/collect-data', { 
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ step: currentStep })
      });

      if (response.ok) {
        const result = await response.json();
        console.log(result);
        setIsCollecting(false);

        if (currentStep < calibrationSteps.length - 1) {
          setCurrentStep(prev => prev + 1);
        } else {
          setProgress(prev => ({ ...prev, calibrationCompleted: true }));
          setCurrentSection('training');
        }
      } else {
        console.error('Error en la captura de datos', await response.json());
        setIsCollecting(false);
      }
    } catch (error) {
      console.error('Error al conectar con Python:', error);
      setIsCollecting(false);
    }
  };
  
  const startTraining = async () => {
    setIsTraining(true);
    const loaderContainer = document.getElementById('loader-container');
    if (loaderContainer) {
      loaderContainer.innerHTML = '<span class="loader"></span>';
    }
  
    try {
      const response = await fetch('http://localhost:5000/api/train-model', { method: 'POST' });
      if (response.ok) {
        const data = await response.json();
        console.log('Entrenamiento completo:', data.result);
        setProgress(prev => ({ ...prev, trainingCompleted: true, modelReady: true }));
  
        // Obtener accuracy actualizado desde la respuesta o fetchAccuracy
        const acc = await fetchAccuracy();
        if (acc !== null) setAccuracy(acc);
      } else {
        console.error('Fallo en el entrenamiento');
      }
    } catch (error) {
      console.error('Error en el entrenamiento:', error);
    } finally {
      if (loaderContainer) loaderContainer.innerHTML = '';
      setIsTraining(false);
    }
  };
  
  const renderCalibrationSection = () => (

    <div className="space-y-6">
      <div className="text-center mb-8">
      <button
      onClick={() => setCurrentSection('menu')}
      className="absolute top-4 left-4 text-slate-600 hover:text-slate-800 transition"
    >
      <ArrowLeftCircle className="w-8 h-8" />
    </button>
        <h2 className="text-2xl font-bold text-slate-800 mb-2">Calibración de la Prótesis</h2>
        <p className="text-slate-600">Paso {currentStep + 1} de 6</p>
      </div>
        <h3 className=" flex justify-center text-xl font-semibold text-slate-800 mb-3 h-2">
          {calibrationSteps[currentStep].movement}
        </h3>
        <p className=" flex justify-center text-slate-600 mb-4 h-8">
          {calibrationSteps[currentStep].description}
        </p>
        <div className="flex justify-center">
          <button
            onClick={startCalibration}
            disabled={isCollecting}
            className={`px-6 py-3 rounded-lg font-semibold transition-all flex items-center gap-2
              ${isCollecting 
                ? 'bg-slate-300 cursor-not-allowed'
                : 'bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white'
              }`}
          >
            {isCollecting ? 'Recolectando datos...' : 'Empezar Calibración'}
            <Sliders className="w-5 h-5" />
          </button>
        </div>

      <div className="flex justify-between mt-4">
        {calibrationSteps.map((step, index) => (
          <div
            key={step.id}
            className={`h-2 w-full mx-1 rounded-full ${
              index < currentStep ? 'bg-green-500' : 
              index === currentStep ? 'bg-blue-500' : 
              'bg-slate-200'
            }`}
          />
        ))}
      </div>
    </div>
  );
  const ToggleSwitch = () => { 
    const [isActive, setIsActive] = useState(true);
    const [showConfirm, setShowConfirm] = useState(false);
  
    const handleClick = () => {
      if (isActive) {
        setShowConfirm(true); // si está encendido, pide confirmación para apagar
      } else {
        setIsActive(true); // si está apagado, se enciende directamente
      }
    };
  
    const confirmPowerOff = async () => {
      try {
        await fetch('http://localhost:5000/api/power-off', {
          method: 'POST',
        });
        setIsActive(false); // apaga si fue exitoso
      } catch (error) {
        console.error('Error al apagar el Myo:', error);
      } finally {
        setShowConfirm(false);
      }
    };
  
    return (
      <div className="flex flex-col items-start mb-4 space-y-2">
        <button onClick={handleClick}>
          <img
            src={`/media/${isActive ? "on" : "off"}.png`}
            alt="Botón de encendido"
            className="w-10 h-10 transition"
          />
        </button>
  
        {showConfirm && (
          <div className="bg-white/80 backdrop-blur-sm shadow-md rounded-lg p-4 text-sm text-slate-800">
            <p className="mb-2">¿Seguro que deseas apagar?</p>
            <div className="flex justify-end space-x-2">
              <button
                onClick={() => setShowConfirm(false)}
                className="px-3 py-1 rounded-md bg-slate-200 hover:bg-slate-300 transition"
              >
                Cancelar
              </button>
              <button
                onClick={confirmPowerOff}
                className="px-3 py-1 rounded-md bg-red-500 text-white hover:bg-red-600 transition"
              >
                Apagar
              </button>
            </div>
          </div>
        )}
      </div>
    );
  };
  

  
  const handleReconnect = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/reconnect', { method: 'POST' });
  
      if (response.ok) {
        const result = await response.json();
        console.log("Reconexión exitosa:", result);
        setIsConnected(true);
      } else {
        const error = await response.json();
        console.error('Error al reconectar:', error);
        setIsConnected(false);
      }
    } catch (error) {
      console.error('Error en la solicitud de reconexión:', error);
      setIsConnected(false);
    }
  };
  

  const renderMainMenu = () => (
    
    
      <div className="space-y-4">
      <div className="absolute top-5 right-5 z-50">
      <div className="absolute -top-3 left-7 z-50">
      <div
        className={`w-4 h-4 rounded-full shadow-md ${
          isConnected === null
            ? 'bg-gray-400'
            : isConnected
            ? 'bg-green-500'
            : 'bg-red-500'
        }`}
        title={isConnected === null ? "Desconocido" : isConnected ? "Conectado" : "Desconectado"}
      ></div>
    </div>

          <button
      onClick={handleReconnect}
      className="bg-white/80 hover:bg-white/90 text-slate-800 p-2 rounded-full shadow-lg transition-all"
      title="Reconectar"
    >
      <RefreshCw className="w-4 h-4" />
    </button>

      </div>

      <ToggleSwitch />
      <h2 className="text-2xl font-bold text-slate-800 mb-2">Panel Principal</h2>
      <p className="text-slate-600 mb-4">
        Aquí puedes calibrar la prótesis, entrenar el modelo de IA y ejecutar el modelo en tiempo real.
      </p>  

      <button
        onClick={() => setCurrentSection('calibration')}
        className="w-full p-4 bg-white rounded-lg shadow-md hover:shadow-lg transition-all flex items-center gap-3"
      >
        <Sliders className="w-6 h-6 text-blue-500" />
        <span className="font-semibold text-slate-800">Calibrar la prótesis</span>
      </button>

      <button
        onClick={() => progress.calibrationCompleted && setCurrentSection('training')}
        className={`w-full p-4 rounded-lg shadow-md transition-all flex items-center gap-3
          ${progress.calibrationCompleted 
            ? 'bg-white hover:shadow-lg cursor-pointer' 
            : 'bg-slate-100 cursor-not-allowed'}`}
      >
        <Brain className={`w-6 h-6 ${progress.calibrationCompleted ? 'text-purple-500' : 'text-slate-400'}`} />
        <span className={`font-semibold ${progress.calibrationCompleted ? 'text-slate-800' : 'text-slate-400'}`}>
          Entrenar el modelo de IA
        </span>
        {!progress.calibrationCompleted && <Lock className="w-4 h-4 ml-auto text-slate-400" />}
      </button>

      <button
        onClick={() => progress.modelReady && setCurrentSection('execution')}
        className={`w-full p-4 rounded-lg shadow-md transition-all flex items-center gap-3
          ${progress.modelReady 
            ? 'bg-white hover:shadow-lg cursor-pointer' 
            : 'bg-slate-100 cursor-not-allowed'}`}
      >
        <Play className={`w-6 h-6 ${progress.modelReady ? 'text-green-500' : 'text-slate-400'}`} />
        <span className={`font-semibold ${progress.modelReady ? 'text-slate-800' : 'text-slate-400'}`}>
          Ejecutar modelo en tiempo real
        </span>
        {!progress.modelReady && <Lock className="w-4 h-4 ml-auto text-slate-400" />}
      </button>
    </div>
  );

  const [showConfirm, setShowConfirm] = useState(false);

  const handleRetrainClick = () => {
    setShowConfirm(true);
  };
  
  const confirmRetraining = () => {
    setShowConfirm(false);
    startTraining();
  };
  
  const cancelRetraining = () => {
    setShowConfirm(false);
  };
  
  const renderTrainingSection = () => (
    <div className="text-center space-y-6">
      <button
        onClick={() => setCurrentSection('menu')}
        className="absolute top-4 left-4 text-slate-600 hover:text-slate-800 transition"
      >
        <ArrowLeftCircle className="w-8 h-8" />
      </button>
      <h2 className="text-2xl font-bold text-slate-800">Entrenamiento de IA</h2>
  
      {!progress.trainingCompleted ? (
        <>
          <p className="text-slate-600 mb-6">
            Los datos de calibración están listos. Inicia el entrenamiento del modelo.
          </p>
  
          <div id="loader-container" className="mb-4 flex justify-center"></div>
  
          <button
            onClick={startTraining}
            disabled={isTraining}
            className={`px-6 py-3 rounded-lg font-semibold transition-all flex items-center gap-2 mx-auto ${
              isTraining
                ? 'bg-slate-300 cursor-not-allowed'
                : 'bg-gradient-to-r from-purple-500 to-indigo-600 hover:from-purple-600 hover:to-indigo-700 text-white'
            }`}
          >
            {isTraining ? 'Entrenando modelo...' : 'Iniciar Entrenamiento'}
            <Brain className="w-5 h-5" />
          </button>
        </>
      ) : (
        <>
          {!isTraining && (
            <>
              <CheckCircle2 className="w-16 h-16 text-blue-500 mx-auto" />
              <p className="text-slate-600">¡El modelo ha sido entrenado exitosamente!</p>
              <p className="text-slate-700 font-medium">
                Precisión del modelo: {accuracy !== null ? `${accuracy}` : '...'}%
              </p>
            </>
          )}
  
          <div id="loader-container" className="mb-4 flex justify-center"></div>
  
          <button
            onClick={handleRetrainClick}
            disabled={isTraining}
            className={`px-6 py-3 rounded-lg font-semibold transition-all flex items-center gap-2 mx-auto ${
              isTraining
                ? 'bg-slate-300 cursor-not-allowed'
                : 'bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white'
            }`}
          >
            {isTraining ? 'Entrenando modelo...' : 'Volver a entrenar el modelo'}
            <Brain className="w-5 h-5" />
          </button>
  
          {showConfirm && (
            <div className="bg-white/90 backdrop-blur-md rounded-lg shadow-lg p-4 w-80 mx-auto mt-4 text-slate-800 text-sm">
              <p className="mb-3">¿Seguro que deseas volver a entrenar el modelo?</p>
              <div className="flex justify-center gap-2">
                <button
                  onClick={cancelRetraining}
                  className="px-4 py-1 rounded-md bg-slate-200 hover:bg-slate-300"
                >
                  Cancelar
                </button>
                <button
                  onClick={confirmRetraining}
                  className="px-4 py-1 rounded-md bg-red-500 text-white hover:bg-red-600"
                >
                  Confirmar
                </button>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
  
  const renderExecutionSection = () => {
    const handleExecutionToggle = () => {
      const mensaje = isRunning ? 'Pausar' : 'Iniciar ejecución';
  
      fetch('http://localhost:5000/api/realtime', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mensaje })
      })
      .then(response => response.json())
      .then(data => {
        console.log('Respuesta de la API:', data);
        setIsRunning(!isRunning);
      })
      .catch(error => {
        console.error('Error al llamar a la API:', error);
      });
    };
  
    return (
      <div className="text-center space-y-6">
        <button
          onClick={() => setCurrentSection('menu')}
          className="absolute top-4 left-4 text-slate-600 hover:text-slate-800 transition"
        >
          <ArrowLeftCircle className="w-8 h-8" />
        </button>
  
        <h2 className="text-2xl font-bold text-slate-800">Ejecución en Tiempo Real</h2>
        <p className="text-slate-600 mb-6">
          El modelo está listo para procesar los movimientos en tiempo real.
        </p>
  
        <button
          onClick={handleExecutionToggle}
          className={`px-6 py-3 text-white rounded-lg font-semibold transition-all flex items-center gap-2 mx-auto ${
            isRunning
              ? 'bg-gradient-to-r from-red-500 to-red-700 hover:from-red-600 hover:to-red-800'
              : 'bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700'
          }`}
        >
          {isRunning ? 'Pausar' : 'Iniciar Ejecución'}
          {isRunning ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5" />}
        </button>
      </div>
    );
  };
  
  return (
    <div className="relative min-h-screen overflow-hidden">
      <div className="absolute inset-0 w-full h-full">
        <video autoPlay loop muted playsInline className="absolute min-w-full min-h-full object-cover">
          <source src="/Media/Fondo.mp4" type="video/mp4" />
        </video>
        <div className="absolute inset-0 bg-black bg-opacity-10" />
      </div>

      <div className="relative min-h-screen flex items-center justify-center p-4">
        <div className="bg-white/30 backdrop-blur-xl rounded-2xl shadow-xl p-8 max-w-md w-full">
          {currentSection === 'menu' && renderMainMenu()}
          {currentSection === 'calibration' && renderCalibrationSection()}
          {currentSection === 'training' && renderTrainingSection()}
          {currentSection === 'execution' && renderExecutionSection()}
        </div>
      </div>
    </div>
  );
}

export default App;
