"use client";

import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { motion, AnimatePresence } from "framer-motion";
import { Upload, FileText, X, CheckCircle, Loader2 } from "lucide-react";

interface FileUploadProps {
  onFileSelect: (file: File) => void;
  isLoading?: boolean;
}

export default function FileUpload({ onFileSelect, isLoading }: FileUploadProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [error, setError] = useState<string>("");

  const onDrop = useCallback(
    (acceptedFiles: File[], rejectedFiles: any[]) => {
      setError("");
      if (rejectedFiles.length > 0) {
        setError("Only PDF files are accepted. Please upload your CAMS statement PDF.");
        return;
      }
      const file = acceptedFiles[0];
      if (!file) return;
      if (file.size > 20 * 1024 * 1024) {
        setError("File too large. Maximum size is 20MB.");
        return;
      }
      setSelectedFile(file);
      onFileSelect(file);
    },
    [onFileSelect]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "application/pdf": [".pdf"] },
    maxFiles: 1,
    disabled: isLoading,
  });

  const clearFile = (e: React.MouseEvent) => {
    e.stopPropagation();
    setSelectedFile(null);
    setError("");
  };

  return (
    <div className="w-full">
      <div
        {...getRootProps()}
        className={`
          relative border-2 border-dashed rounded-2xl p-10 text-center cursor-pointer
          transition-all duration-300 outline-none
          ${isDragActive ? "dropzone-active border-brand-400" : "border-dark-400 hover:border-dark-300"}
          ${isLoading ? "opacity-60 cursor-not-allowed" : ""}
          ${selectedFile ? "border-brand-500 bg-brand-500/5" : "bg-dark-800/50"}
        `}
      >
        <input {...getInputProps()} />

        <AnimatePresence mode="wait">
          {isLoading ? (
            <motion.div
              key="loading"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex flex-col items-center gap-4"
            >
              <div className="w-16 h-16 rounded-2xl bg-brand-500/10 flex items-center justify-center">
                <Loader2 className="w-8 h-8 text-brand-400 animate-spin" />
              </div>
              <div>
                <p className="text-white font-semibold text-lg">Analyzing your portfolio…</p>
                <p className="text-gray-400 text-sm mt-1">Running XIRR, overlap, tax & goal calculations</p>
              </div>
              {/* Progress steps */}
              <div className="flex items-center gap-2 text-xs text-gray-500">
                {["Parsing PDF", "Fetching NAV", "Calculating XIRR", "AI Insights"].map((step, i) => (
                  <span key={step} className="flex items-center gap-1">
                    {i > 0 && <span className="text-dark-400">→</span>}
                    <span className="text-brand-400">{step}</span>
                  </span>
                ))}
              </div>
            </motion.div>
          ) : selectedFile ? (
            <motion.div
              key="selected"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0 }}
              className="flex flex-col items-center gap-4"
            >
              <div className="w-16 h-16 rounded-2xl bg-brand-500/15 flex items-center justify-center animate-glow">
                <CheckCircle className="w-8 h-8 text-brand-400" />
              </div>
              <div>
                <p className="text-white font-semibold">{selectedFile.name}</p>
                <p className="text-gray-400 text-sm mt-1">
                  {(selectedFile.size / 1024).toFixed(0)} KB · Ready to analyze
                </p>
              </div>
              <button
                onClick={clearFile}
                className="flex items-center gap-1.5 text-gray-500 hover:text-red-400 text-xs transition-colors"
              >
                <X className="w-3 h-3" /> Remove file
              </button>
            </motion.div>
          ) : (
            <motion.div
              key="idle"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex flex-col items-center gap-4"
            >
              <div
                className={`w-16 h-16 rounded-2xl flex items-center justify-center transition-all duration-300 ${
                  isDragActive ? "bg-brand-500/20 scale-110" : "bg-dark-600"
                }`}
              >
                {isDragActive ? (
                  <FileText className="w-8 h-8 text-brand-400" />
                ) : (
                  <Upload className="w-8 h-8 text-gray-400" />
                )}
              </div>
              <div>
                <p className="text-white font-semibold text-lg">
                  {isDragActive ? "Drop your CAMS PDF here" : "Upload CAMS Statement"}
                </p>
                <p className="text-gray-400 text-sm mt-1">
                  Drag & drop or{" "}
                  <span className="text-brand-400 underline underline-offset-2">click to browse</span>
                </p>
                <p className="text-gray-600 text-xs mt-3">
                  PDF only · Max 20MB · 100% processed in-memory, never stored
                </p>
              </div>

              {/* How to get CAMS */}
              <div className="mt-2 px-4 py-3 rounded-xl bg-dark-700 border border-dark-500 text-left">
                <p className="text-xs text-gray-400 font-medium mb-1.5">📄 How to get your CAMS statement</p>
                <ol className="text-xs text-gray-500 space-y-1 list-decimal list-inside">
                  <li>Visit <span className="text-brand-400">camsonline.com</span> → Mail Back Services</li>
                  <li>Enter PAN, email → request Detailed Statement</li>
                  <li>Download the PDF from your email</li>
                </ol>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {error && (
        <motion.p
          initial={{ opacity: 0, y: -4 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-2 text-red-400 text-sm text-center"
        >
          ⚠️ {error}
        </motion.p>
      )}
    </div>
  );
}
