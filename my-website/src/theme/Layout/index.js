import React from 'react';
import BrowserOnly from '@docusaurus/BrowserOnly';
import OriginalLayout from '@theme-original/Layout';
import Chatbot from '@site/src/components/Chatbot';

export default function LayoutWrapper(props) {
  return (
    <OriginalLayout {...props}>
      {props.children}
      <BrowserOnly>
        {() => <Chatbot />}
      </BrowserOnly>
    </OriginalLayout>
  );
}