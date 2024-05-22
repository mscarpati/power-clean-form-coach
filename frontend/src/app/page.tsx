"use client";
import { useState, useEffect } from "react";
import UploadForm from "./components/uploadForm";

// Ideas & todos

// Typing animation for title
// Only show other stuff on scroll
// Scroll to learn more is like bouncing arrow can deal with animations later
// Demo video before and after maybe?
// Upon bar path analysis, explain that there should be little to no movement in bar path
// Upon form analysis, explain significance of different circle colors and how criteria is met

export default function Home() {
  const [lastScrollY, setLastScrollY] = useState(0);
  const [atTop, setAtTop] = useState(true);
  const [show, setShow] = useState(false);

  const control = () => {
    if (typeof window !== "undefined") {
      if ((window.scrollY > lastScrollY && !atTop) || (window.scrollY < lastScrollY && !atTop)) {
        setShow(true)
      } else if (atTop) {
        setShow(false)
      }
    }

    setLastScrollY(window.scrollY);

    
    if (window.scrollY > 360) {
      setAtTop(true);
    } else {
      setAtTop(false);
    }
    console.log("scrolling");
  };

  useEffect(() => {
    if (typeof window !== 'undefined') {
      window.addEventListener('scroll', control);
      console.log("use effect");
    }


    return () => {
      window.removeEventListener('scroll', control);
    };

  }, [lastScrollY, control]);

  return (
    <div className="relative flex min-h-screen flex-col items-center p-24">
      {/* <div className="absolute inset-0 z-0 flex-grow">
        <Image
          src="/gym.jpg"
          layout="fill"
          alt='gym'
          objectFit="cover"
          quality={100}
          style={{ opacity: '0.5' }}
        />
      </div> */}
      <div className="relative z-10">
        <div className={`active ${show ? 'transition-all duration-500' : 'transition-all duration-500 opacity-0'}`}>
        <h2 className='text-6xl font-bold typing-effect'>
          Welcome to Form Coach for Power Clean.
        </h2>
        <div className='mt-6'>
        <p className='text-3xl'>Scroll to learn more.</p>
        </div>
        
        <div className='animate-bounce hover:scale-110'>
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-20 h-20">
            <path strokeLinecap="round" strokeLinejoin="round" d="m19.5 8.25-7.5 7.5-7.5-7.5" />
          </svg>
        </div>
        </div>
        <div className='h-80'>
        <p></p>
        </div>
        <div className='h-80'>
        <p></p>
        </div>
        <div className={`active ${!show ? 'transition-all duration-500' : 'transition-all duration-500 opacity-0'}`}>
        <div>
          <p className='text-lg mt-10 mb-6'>
            Without a trainer, it can be difficult to perform the power clean safely and effectively.
            Bar path and joint extension timing are crucial for a successful and safe lift. It's nearly impossible to assess that on your own.
            By uploading video footage, this web application can analyze your form using computer vision.
            Continue scrolling to test it out.
          </p>
        </div>
        <div>
          <p className='text-lg'>
            Any lift can be uploaded through the bar path model. The form analysis model is specific to the power clean.
            For best results, your video should be taken at a 3/4 frontal view.
          </p>
        </div>
        </div>
        {/* example here before and after */}
        <div className='mt-10'>
        <UploadForm />
        </div>
        <div className='h-80'>
        <p></p>
        </div>
      </div>
    </div>
  );
}
