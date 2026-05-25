import { useCallback, useState } from 'react';
import { api } from '../api/client';
import type { Document } from '../types';

interface UseDocumentsReturn {
  documents: Document[];
  uploading: boolean;
  upload: (file: File) => Promise<Document>;
  remove: (id: string) => Promise<void>;
  clear: () => void;
}

export function useDocuments(): UseDocumentsReturn {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [uploading, setUploading] = useState(false);

  const upload = useCallback(async (file: File): Promise<Document> => {
    setUploading(true);
    try {
      const doc = await api.uploadDocument(file);
      setDocuments((prev) => [...prev, doc]);
      return doc;
    } finally {
      setUploading(false);
    }
  }, []);

  const remove = useCallback(async (id: string) => {
    await api.deleteDocument(id);
    setDocuments((prev) => prev.filter((d) => d.id !== id));
  }, []);

  const clear = useCallback(() => setDocuments([]), []);

  return { documents, uploading, upload, remove, clear };
}
