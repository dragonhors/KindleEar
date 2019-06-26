#!/bin/bash

# ------------------------------------------
# 名称：KindleEar安装脚本
# 作者：bookfere.com
# 页面：https://bookfere.com/post/19.html
# 更新：2018.04.18
# ------------------------------------------
# 目录切到当前用户的工作目录
cd ~

# 查看是否已有KindleEar项目库目录
if [ ! -d "./KindleEar" ]
then
#没有就从github网站克隆一整个
    git clone https://github.com/dragonhors/KindleEar.git
else
#有就确认一下是否更新？
    response='y'
    read -r -p '已存在 KindleEar 源码，是否更新？[y/N]' response
    if [[ $response =~ ^([yY][eE][sS]|[yY])$ ]]
    then
        if [[ ! -d "./KindleEar/.git" ]]
		#如果没有git库就删掉重新克隆，
        then
            rm -rf ./KindleEar
            git clone https://github.com/dragonhors/KindleEar.git
        else
		#已有git库，就更新一下代码
            cd ./KindleEar
            git pull
            cd ..
        fi
    fi
fi

#切换到kindleEar目录下，准备执行最后面的两条指令进行升级，因为这两条指令文件在这个目录中，这两条指令也是upload.sh文件的主体。
cd KindleEar

#下面的这些在升级过程中可以按提示操作，没必要提前修正，还增加了编程错误风险和调试工作量
cemail=$(sed -n "s/^SRC_EMAIL\ =\ \"\(.*\)\".*#.*/\1/p" ./config.py)
cappid=$(sed -n "s/^DOMAIN\ =\ \"http\(\|s\):\/\/\(.*\)\.appspot\.com\/\".*#.*/\2/p" ./config.py)
response='y'

echo '当前的 Gmail 为：'$cemail
echo '当前的 APPID 为：'$cappid

if [ ! $cemail = "akindleear@gmail.com" -o ! $cappid = "kindleear" ]
then
    read -r -p "是否修改 APP 信息? [y/N] " response
fi

if [[ $response =~ ^([yY][eE][sS]|[yY])$ ]]
then
    echo -n "请输入你的 Gmail 地址："
    read email
    echo "您输入的 Gmail 地址是：'$email'"
    sed -i "s/^SRC_EMAIL = \".*\"/SRC_EMAIL = \"$email\"/g" ./config.py
    echo -n "请输入你的 APP ID："
    read appid
    echo "您输入的 APP ID 是：'$appid'"
    sed -i "s/^application: .*/application: $appid/g" ./app.yaml ./module-worker.yaml
    sed -i "s/^DOMAIN = \"http\(\|s\):\/\/.*\.appspot\.com\/\"/DOMAIN = \"http:\/\/$appid\.appspot\.com\/\"/g" ./config.py
fi

#更新KindleEar执行系统配置？
appcfg.py update app.yaml module-worker.yaml --no_cookie --noauth_local_webserver
appcfg.py update . --no_cookie --noauth_local_webserver