// src/setupTests.ts
import '@testing-library/jest-dom/vitest';
import React from 'react';

// Force the test environment to use the same React instance
global.React = React;
