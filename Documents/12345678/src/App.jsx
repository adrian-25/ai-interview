import PixelBlast from './reactbits/PixelBlast';
import ClickSpark from './reactbits/ClickSpark';
import Nav from './sections/Nav';
import Hero from './sections/Hero';
import HowItWorks from './sections/HowItWorks';
import Conditions from './sections/Conditions';
import Why from './sections/Why';
import Footer from './sections/Footer';
import useReducedMotion from './useReducedMotion';
import './App.css';

function App() {
  const reducedMotion = useReducedMotion();

  return (
    <>
      {/* Persistent, full-page pixel blast — mounted once, behind everything. */}
      <div className="galaxy-layer" aria-hidden="true">
        <PixelBlast
          variant="square"
          pixelSize={4}
          color="#B497CF"
          patternScale={2}
          patternDensity={1}
          enableRipples={!reducedMotion}
          rippleSpeed={0.3}
          rippleThickness={0.1}
          rippleIntensityScale={1}
          speed={reducedMotion ? 0 : 0.5}
          edgeFade={0.25}
          transparent
        />
      </div>

      {/* Global click sparks — render above all content, site-wide. */}
      <ClickSpark
        sparkColor="#FF3B4E"
        sparkSize={10}
        sparkRadius={18}
        sparkCount={8}
        duration={450}
      >
        <div className="page">
          <Nav />
          <main>
            <Hero />
            <HowItWorks />
            <Conditions />
            <Why />
          </main>
          <Footer />
        </div>
      </ClickSpark>
    </>
  );
}

export default App;
