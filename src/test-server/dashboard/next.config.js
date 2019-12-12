const withCSS = require('@zeit/next-css')

require('dotenv')
  .config()

const path = require('path')
const Dotenv = require('dotenv-webpack')

module.exports = withCSS({
  webpack: config => {
    // Fixes npm packages that depend on non-universal modules
    // ref: https://github.com/zeit/next.js/issues/2734
    // ref: https://azure.microsoft.com/ja-jp/blog/azure-cosmos-now-supports-cross-origin-resource-sharing-cors/
    config.node = {
      fs: 'empty',
      net: 'mock',
      tls: 'mock',
    }

    config.plugins = config.plugins || []

    config.plugins = [
      ...config.plugins,

      // Read the .env file
      new Dotenv({
        path: path.join(__dirname, '.env'),
        systemvars: true,
      }),
    ]

    return config
  },
})
