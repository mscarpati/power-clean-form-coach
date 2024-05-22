'use client';

import axios from 'axios';
import { useState } from 'react';
import { Button } from '@chakra-ui/react';

interface AnalyzedVideoProps {
    filename: string;
}

const AnalyzedVideo = ({filename}: AnalyzedVideoProps) => {
    const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL;
    const [show, setShow] = useState(false);
    const videoUrl = `${apiBaseUrl}/results/${filename}`;

    return (
        <div className='mt-2'>
            <Button onClick={() => setShow(true)}>Get Your Results!</Button>
            {show && videoUrl && <video width="640" height="360" src={videoUrl} controls></video>}
        </div>
    )
};
export default AnalyzedVideo;