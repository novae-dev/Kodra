import React, { useState, useEffect } from "react";
import { Settings, X } from "lucide-react";
import { KodraApi } from "../services/api";

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
  activeProvider: string;
  onProviderChanged: (newProvider: string) => void;
}

export const SettingsModal: React.FC<SettingsModalProps> = ({
  isOpen,
  onClose,
  activeProvider,
  onProviderChanged,
}) => {
  const [provider, setProvider] = useState(activeProvider);
  const [model, setModel] = useState("");
  const [apiKey, setApiKey] = useState("");
  const [ollamaHost, setOllamaHost] = useState("http://localhost:11434");
  const [loading, setLoading] = useState(false);
  const [statusMsg, setStatusMsg] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen) {
      KodraApi.getConfig()
        .then((cfg) => {
          setProvider(cfg.provider || "mock");
          setModel(cfg.model || "");
          setOllamaHost(cfg.ollama_host || "http://localhost:11434");
        })
        .catch(() => {});
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setStatusMsg(null);
    try {
      const payload: Record<string, any> = {
        provider,
        model: model || null,
      };

      if (provider === "openai" && apiKey) {
        payload.openai_api_key = apiKey;
      } else if (provider === "anthropic" && apiKey) {
        payload.anthropic_api_key = apiKey;
      } else if (provider === "gemini" && apiKey) {
        payload.gemini_api_key = apiKey;
      } else if (provider === "groq" && apiKey) {
        payload.groq_api_key = apiKey;
      } else if (provider === "ollama") {
        payload.ollama_host = ollamaHost;
      }

      await KodraApi.updateConfig(payload);
      onProviderChanged(provider);
      setStatusMsg("Settings successfully saved!");
      setTimeout(() => {
        onClose();
        setStatusMsg(null);
      }, 700);
    } catch (err: any) {
      setStatusMsg(`Error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-dialog" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div className="modal-title">
            <Settings size={16} color="#818cf8" />
            <span>AI Provider & Model Settings</span>
          </div>
          <button className="icon-mini-btn" onClick={onClose}>
            <X size={15} />
          </button>
        </div>

        <form onSubmit={handleSave} className="modal-body">
          <label className="input-label">Select Active AI Provider:</label>
          <select
            className="text-input"
            value={provider}
            onChange={(e) => setProvider(e.target.value)}
          >
            <option value="mock">Local Mock Provider (Built-in, zero keys needed)</option>
            <option value="openai">OpenAI (GPT-4o, GPT-4o-mini)</option>
            <option value="anthropic">Anthropic (Claude 3.5 Sonnet)</option>
            <option value="gemini">Google Gemini (Gemini 2.5 Flash, 1.5 Pro)</option>
            <option value="groq">Groq (Llama-3.3-70B Fast Inference)</option>
            <option value="ollama">Ollama (Local Models)</option>
          </select>

          {provider !== "mock" && provider !== "ollama" && (
            <>
              <label className="input-label">
                API Key for {provider.toUpperCase()}:
              </label>
              <input
                type="password"
                className="text-input"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                placeholder="Leave blank to use environment variable"
              />
            </>
          )}

          {provider === "ollama" && (
            <>
              <label className="input-label">Ollama Host URL:</label>
              <input
                type="text"
                className="text-input"
                value={ollamaHost}
                onChange={(e) => setOllamaHost(e.target.value)}
                placeholder="http://localhost:11434"
              />
            </>
          )}

          <label className="input-label">Custom Model Override (optional):</label>
          <input
            type="text"
            className="text-input"
            value={model}
            onChange={(e) => setModel(e.target.value)}
            placeholder="e.g. gpt-4o, claude-3-5-sonnet-20241022, deepseek-coder"
          />

          {statusMsg && <div className="modal-status-msg">{statusMsg}</div>}

          <div className="modal-footer">
            <button type="button" className="btn secondary" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="btn primary" disabled={loading}>
              {loading ? "Saving..." : "Save Settings"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
