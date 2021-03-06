var path = require("path");
var webpack = require("webpack");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");


const config = {
	// Common Configuration
	module: {
	    rules: [
	        {
		        test:/\.css$/,
	            use:
	            	[
	            		'style-loader',
          				MiniCssExtractPlugin.loader, // evtl sinnlos ? funktioniert auch ohne
  		                'css-loader'
	            	]
	        },
	        {
	        	test: /\.(jpg|png|gif)$/,
	        	use: [
	        		{
	        			loader: "file-loader",
	        			options: {
	        				name: '[name].[ext]',
	        				outputPath: 'img/',
	        				publicPath: 'img/'
	        			}
	        		}
	        	]
	        },
	        {
	        	test: /\.html$/,
	        	use: ["html-loader"]
	        },
  	        {
	          test: /\.(woff(2)?|ttf|eot|svg)$/,
	          use: [
	            {
	              loader: 'file-loader',
                  options: {
                        name: '[name].[ext]',
                        outputPath: 'fonts/',
						publicPath: 'fonts/'

                  },
	            },
	          ]
	        },
	        {
	        	test: /\.js$/,
			    exclude: /(node_modules|bower_components)/,
	        	use: [
	        		{
	        			loader: "babel-loader",
	        			options: {
	        				presets: ["@babel/preset-env"]
	        			}
	        		}
	        	]
	        },
			{
				test: /modernizr/,
				loader: 'imports-loader?this=>window!exports-loader?window.Modernizr'
			}
		]
	},
	plugins: [
		// ~/vendor/fullcalendar/3.10.0/lib/jquery.min.js
		new webpack.ProvidePlugin({
			//$: path.resolve(__dirname, "~/vendor/jquery/jquery.min.js"),
			//jQuery: path.resolve(__dirname, "~/vendor/jquery/jquery.min.js")
			//moment: path.resolve(__dirname, "src/vendor/moment/moment.min.js")
			// $: "jquery",
			// jQuery: "jquery"
		}),
	    new MiniCssExtractPlugin({  // Evtl sinnlos ? funktioniert auch ohne
	      filename: "[name].css",
    	  chunkFilename: "[id].css"
    	})
		//, new CleanWebpackPlugin(["dist"])
	],
	resolve: {
		extensions: [".js"],
		alias: {
			"~": path.resolve(__dirname, "./src")
		}
	},

};

const baseConfig = Object.assign({}, config, {
	entry: {
		"bundle": "./src/base/js/app.js"
	},
	output: {
		path: path.resolve(__dirname, "../static/dist/base/"),
		filename: "[name].js",
		publicPath: "/build/base/"
	},
    devServer: {
		headers: {
			"Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, PATCH, OPTIONS",
			"Access-Control-Allow-Headers": "X-Requested-With, content-type, Authorization",
			"Access-Control-Allow-Origin": "*"
		}
  	}
})


const accountUserListConfig = Object.assign({}, config, {
	entry: {
		bundle: "./src/account/user_list/js/app.js"
	},
	output: {
		path: path.resolve(__dirname, "../static/dist/account/user_list/"),
		filename: "[name].js",
		publicPath: "/build/account/user_list/"
	}
})


const accountAuthorizationConfig = Object.assign({}, config, {
	entry: {
		bundle: "./src/account/authorization/js/app.js"
	},
	output: {
		path: path.resolve(__dirname, "../static/dist/account/authorization/"),
		filename: "[name].js",
		publicPath: "/build/account/authorization/"
	}
})


const accountGroupListConfig = Object.assign({}, config, {
	entry: {
		bundle: "./src/account/group_list/js/app.js"
	},
	output: {
		path: path.resolve(__dirname, "../static/dist/account/group_list/"),
		filename: "[name].js",
		publicPath: "/build/account/group_list/"
	}
})


const appointmentConfig = Object.assign({}, config, {
	entry: {
		bundle: ["./src/appointment/base/js/app.js", "./src/appointment/base/js/datetimepicker.js",
				 "./src/appointment/base/js/fullcalendar.js"],
	},
	//	    "~/vendor/bootstrap-datetimepicker/4.17.47/build/js/bootstrap-datetimepicker.min.js"
	output: {
		path: path.resolve(__dirname, "../static/dist/appointment/base/"),
		filename: "[name].js",
		publicPath: "/build/appointment/base/"
	}
})


const dutyRosterConfig = Object.assign({}, config, {
	entry: {
		bundle: ["./src/appointment/duty_roster/js/app.js",],
	},
	//	    "~/vendor/bootstrap-datetimepicker/4.17.47/build/js/bootstrap-datetimepicker.min.js"
	output: {
		path: path.resolve(__dirname, "../static/dist/appointment/duty_roster/"),
		filename: "[name].js",
		publicPath: "/build/appointment/duty_roster/"
	}
})



const filestorageConfig = Object.assign({}, config, {
	entry: {
		bundle: ["./src/filestorage/js/app.js"],
	},
	//	    "~/vendor/bootstrap-datetimepicker/4.17.47/build/js/bootstrap-datetimepicker.min.js"
	output: {
		path: path.resolve(__dirname, "../static/dist/filestorage/"),
		filename: "[name].js",
		publicPath: "/build/filestorage/"
	}
})


const filestorageEditConfig = Object.assign({}, config, {
	entry: {
		bundle: ["./src/filestorage/js/edit.js"],
	},
	//	    "~/vendor/bootstrap-datetimepicker/4.17.47/build/js/bootstrap-datetimepicker.min.js"
	output: {
		path: path.resolve(__dirname, "../static/dist/filestorage/edit/"),
		filename: "[name].js",
		publicPath: "/build/filestorage/edit/"
	}
})


const taskManagementConfig = Object.assign({}, config, {
	entry: {
		bundle: ["./src/taskmanagement/js/app.js"],
	},
	output: {
		path: path.resolve(__dirname, "../static/dist/taskmanagement/"),
		filename: "[name].js",
		publicPath: "/build/taskmanagement/"
	}
})


const accomplishmentConfig = Object.assign({}, config, {
	entry: {
		bundle: ["./src/accomplishment/list/js/app.js"],
	},
	output: {
		path: path.resolve(__dirname, "../static/dist/accomplishment/list/"),
		filename: "[name].js",
		publicPath: "/build/accomplishment/list/"
	}
})


const phoneBookConfig = Object.assign({}, config, {
	entry: {
		bundle: ["./src/phonebook/js/app.js"],
	},
	output: {
		path: path.resolve(__dirname, "../static/dist/phonebook/"),
		filename: "[name].js",
		publicPath: "/build/phonebook/"
	}
})


const phoneBookCategoryConfig = Object.assign({}, config, {
	entry: {
		bundle: ["./src/phonebook-category/js/app.js"],
	},
	output: {
		path: path.resolve(__dirname, "../static/dist/phonebook-category/"),
		filename: "[name].js",
		publicPath: "/build/phonebook-category/"
	}
})


const subjectAreaConfig = Object.assign({}, config, {
	entry: {
		bundle: ["./src/subject_area/js/app.js"],
	},
	output: {
		path: path.resolve(__dirname, "../static/dist/subject_area/"),
		filename: "[name].js",
		publicPath: "/build/subject_area/"
	}
})


const subjectAreaEditConfig = Object.assign({}, config, {
	entry: {
		bundle: ["./src/subject_area/edit/js/app.js"],
	},
	output: {
		path: path.resolve(__dirname, "../static/dist/subject_area/edit/"),
		filename: "[name].js",
		publicPath: "/build/subject_area/edit/"
	}
})

const PollConfig = Object.assign({}, config, {
	entry: {
		bundle: ["./src/poll/js/app.js"],
	},
	output: {
		path: path.resolve(__dirname, "../static/dist/poll/"),
		filename: "[name].js",
		publicPath: "/build/poll/"
	}
})



const PollOptionEditConfig = Object.assign({}, config, {
	entry: {
		bundle: ["./src/poll/option/edit/js/app.js"],
	},
	output: {
		path: path.resolve(__dirname, "../static/dist/poll/option/edit/"),
		filename: "[name].js",
		publicPath: "/build/poll/option/edit/"
	}
})

const ProposalTypeConfig = Object.assign({}, config, {
	entry: {
		bundle: ["./src/proposal/type/js/app.js"],
	},
	output: {
		path: path.resolve(__dirname, "../static/dist/proposal/type/"),
		filename: "[name].js",
		publicPath: "/build/proposal/type/"
	}
})

const ProposalConfig = Object.assign({}, config, {
	entry: {
		bundle: ["./src/proposal/js/app.js"],
	},
	output: {
		path: path.resolve(__dirname, "../static/dist/proposal/"),
		filename: "[name].js",
		publicPath: "/build/proposal/"
	}
})



module.exports = [
	baseConfig,
	accountUserListConfig,
	accountAuthorizationConfig,
	appointmentConfig,
	dutyRosterConfig,
	filestorageConfig,
	filestorageEditConfig,
	accountGroupListConfig,
	taskManagementConfig,
	accomplishmentConfig,
	phoneBookConfig,
	phoneBookCategoryConfig,
	subjectAreaConfig,
	subjectAreaEditConfig,
	PollConfig,
	PollOptionEditConfig,
	ProposalTypeConfig,
	ProposalConfig
]
