import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, X, CheckCircle } from 'lucide-react';
import { uploadFiles } from '../api/client';

function FileUploader({ onUploadComplete }) {
    const [uploading, setUploading] = useState(false);
    const [uploadedFiles, setUploadedFiles] = useState([]);
    const [error, setError] = useState(null);

    const onDrop = useCallback(async (acceptedFiles) => {
        if (acceptedFiles.length === 0) return;

        setUploading(true);
        setError(null);

        try {
            const result = await uploadFiles(acceptedFiles);
            setUploadedFiles(prev => [...prev, ...result.uploaded]);
            if (onUploadComplete) {
                onUploadComplete(result);
            }
        } catch (err) {
            setError(err.response?.data?.detail || 'Upload failed');
        } finally {
            setUploading(false);
        }
    }, [onUploadComplete]);

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: { 'application/pdf': ['.pdf'] },
        multiple: true,
    });

    const removeFile = (index) => {
        setUploadedFiles(prev => prev.filter((_, i) => i !== index));
    };

    const formatFileSize = (bytes) => {
        if (bytes < 1024) return `${bytes} B`;
        if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
        return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
    };

    return (
        <div>
            <div
                {...getRootProps()}
                className={`dropzone ${isDragActive ? 'active' : ''}`}
            >
                <input {...getInputProps()} />
                <div className="dropzone-icon">
                    {uploading ? (
                        <div className="spinner" style={{ width: 40, height: 40 }} />
                    ) : (
                        <Upload size={48} strokeWidth={1.5} />
                    )}
                </div>
                <div className="dropzone-text">
                    {isDragActive
                        ? 'Drop your PDFs here...'
                        : uploading
                            ? 'Uploading files...'
                            : 'Drag & drop ESG reports here'}
                </div>
                <div className="dropzone-subtext">
                    or click to browse • PDF files only
                </div>
            </div>

            {error && (
                <div style={{
                    marginTop: 'var(--space-3)',
                    padding: 'var(--space-3) var(--space-4)',
                    background: 'rgba(244, 63, 94, 0.1)',
                    borderRadius: 'var(--radius-lg)',
                    color: 'var(--rose-400)',
                    fontSize: '0.85rem',
                }}>
                    ⚠️ {error}
                </div>
            )}

            {uploadedFiles.length > 0 && (
                <div className="file-list">
                    {uploadedFiles.map((file, index) => (
                        <div key={index} className="file-item animate-in">
                            <div className="file-info">
                                <div className="file-icon">
                                    <FileText size={16} />
                                </div>
                                <div>
                                    <div className="file-name">{file.filename}</div>
                                    <div className="file-size">{formatFileSize(file.size_bytes)}</div>
                                </div>
                            </div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
                                <CheckCircle size={16} color="var(--emerald-500)" />
                                <button
                                    className="btn btn-icon btn-secondary"
                                    onClick={(e) => { e.stopPropagation(); removeFile(index); }}
                                    title="Remove"
                                >
                                    <X size={14} />
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}

export default FileUploader;
