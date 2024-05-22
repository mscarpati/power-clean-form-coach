'use client';

import { Button, Input, VStack, Stack, CircularProgress } from '@chakra-ui/react';
import axios from 'axios';
import React, { useState } from 'react';

import AnalyzedVideo from './analyzedVideo';
import LoadingCircle from "./loadingCircle";
import VideoCanvas from './videoCanvas';

const UploadForm: React.FC = () => {
  const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL;
  const [file, setFile] = useState<File | null>(null);
  const [barTracker, setBarTracker] = useState<boolean>(false);
  const [formAnalysis, setFormAnalysis] = useState<boolean>(false);
  const [showResultsButton, setShowResultsButton] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(false);
  const [inputVideoUrl, setInputVideoUrl] = useState<string>('');

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      setFile(event.target.files[0]);
    } else {
      setFile(null);
    }
  }

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!file) {
      alert('Please select a file to upload');
      return;
    }
    if (!barTracker && !formAnalysis) {
      alert('Please select at least one analysis type');
      return;
    }
    const formData = new FormData();
    formData.append('file', file);
    formData.append('barTracker', barTracker.toString());
    formData.append('formAnalysis', formAnalysis.toString());
    setLoading(true);
    try {
      const response = await axios.post(`${apiBaseUrl}/upload`, formData);
      alert('File uploaded successfully!');
      setShowResultsButton(true);
      setInputVideoUrl(`${apiBaseUrl}/inputs/${file?.name}`);
      console.log('Upload response:', response.data);
    } catch (error) {
      alert('Error uploading file');
      console.error('Upload error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <VStack spacing={4} align="stretch">
          <Input type="file" accept="video/*" onChange={handleFileChange} padding={1} borderColor="gray.400" />
          <p className='font-bold'>Select model(s):</p>
          <div className='pl-2'>
            <Stack direction='row' spacing={4}>
              <Input className='mt-1 hover:cursor-pointer' type='checkbox' onChange={(e) => setBarTracker(!barTracker)} />
              <p className={`${barTracker ? 'font-bold' : ''} mb-1'`}>Bar Tracker</p>
            </Stack>
            <Stack direction='row' spacing={4}>
              <Input className='mt-1 hover:cursor-pointer' type='checkbox' onChange={(e) => setFormAnalysis(!formAnalysis)} />
              <p className={`${formAnalysis ? 'font-bold' : ''} mb-1'`}>Form Analysis</p>
            </Stack>
          </div>
          <Button className='w-[10%] rounded-lg hover:scale-110 bg-blue hover:bg-dark-blue' colorScheme="blue" type="submit">Upload Video</Button>
        </VStack>
      </form>
      {loading &&
        <div className='flex-row'>
          <LoadingCircle />
          <p>Uploading...</p>
        </div>
      }
      {inputVideoUrl && barTracker &&
      <VideoCanvas videoUrl={inputVideoUrl} setLoading={setLoading} />}
      {showResultsButton && <AnalyzedVideo filename={`${file?.name.split('.')[0]}-out.mp4`} />}
    </div>
  );
};

export default UploadForm;