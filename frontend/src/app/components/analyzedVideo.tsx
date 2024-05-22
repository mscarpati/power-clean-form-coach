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
            {show && videoUrl && 
            <div className = 'flex flex-row px-10'>
            <video width="640" height="360" src={videoUrl} controls>
                </video>
                <p className='text-white w-[50%] mx-10 my-20'>An ideal bar path will have little to no movement outside of a straight line up and down.
                The key points for pose detection are knee angle at the landing and hip angle at the hip hinge midway through the lift. 
                A yellow circle around this joint indicates your angles were within two standard deviations of the optimal angle (derived from professional lifts). Orange means you were within three, and red is anything above that.</p>
                </div>}
        </div>
    )
};
export default AnalyzedVideo;