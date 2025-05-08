
def run(stl_path,gcode_path):
    import subprocess
    import slicer
    import os
    from stl import mesh
    import numpy as np
    import slicer.util as util
    util.send_event_str(util.ProgressStart,"正在进行模型切片")
    # 读取STL文件
    your_mesh = mesh.Mesh.from_file(stl_path)

    # 计算模型的尺寸
    minx, maxx, miny, maxy, minz, maxz = np.inf, -np.inf, np.inf, -np.inf, np.inf, -np.inf
    for v in your_mesh.vectors:
        minx = min(minx, v[:,0].min())
        maxx = max(maxx, v[:,0].max())
        miny = min(miny, v[:,1].min())
        maxy = max(maxy, v[:,1].max())
        minz = min(minz, v[:,2].min())
        maxz = max(maxz, v[:,2].max())

    # 计算需要移动的距离以将模型中心移至原点
    move_x = -(minx + (maxx - minx) / 2)
    move_y = -(miny + (maxy - miny) / 2)
    move_z = -minz  # 通常 Z 轴不需要调整，除非需要模型底部与打印平台表面对齐

    # 更新模型的位置
    your_mesh.translate([move_x, move_y, move_z])

    # 保存修改后的STL文件
    your_mesh.save(stl_path)

    project_path = slicer.app.applicationDirPath()
    
    # 设置CuraEngine的路径
    cura_engine_path = project_path+'/UltiMakerCura/CuraEngine'

    # STL文件的路径
    stl_file = stl_path

    # 输出G-code文件的路径
    gcode_file = gcode_path
    import os
    # 配置文件的路径
    #config_file = project_path+'/UltiMakerCura/resources/definitions/ultimaker_s4.def.json'
    config_file = project_path+'/UltiMakerCura/resources/definitions/xiaoluban1.json'
    # 构建命令行命令
    command = [
      cura_engine_path,
      'slice',
      '-v',
      '-p',
      '-s', 'support_enable=true',
      '-s', 'roofing_layer_count=3',
      '-j', config_file,  # 加载配置文件
      '-l', stl_file,  # 加载STL文件
      '-o', gcode_file  # 输出G-code文件
    ]
    
    # 调用CuraEngine
    #result = subprocess.run(command, capture_output=True, encoding='utf-8', text=True)
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8', text=True)
    import re
    pattern = re.compile(r"GcodeWriter processing layer (\d+) of (\d+)")
    # 逐行读取标准输出和标准错误
    for stdout_line in iter(process.stdout.readline, ""):
        print(stdout_line, end="")  # 实时打印标准输出
        match = pattern.search(stdout_line)
        if match:
            layer_num = match.group(1)
            total_layers = match.group(2)
            util.send_event_str(util.ProgressValue,int(int(layer_num)*100/int(total_layers)))
        if stdout_line == '' and process.poll() is not None:
            break
        
    # 逐行读取标准输出和标准错误
    # while True:
    #     stdout_line = process.stdout.readline()
    #     if stdout_line == '' and process.poll() is not None:
    #         break
    #     if stdout_line:
    #         print(stdout_line, end="")  # 实时打印标准输出
    #         match = pattern.search(stdout_line)
    #         if match:
    #             layer_num = match.group(1)
    #             total_layers = match.group(2)
    #             util.send_event_str(util.ProgressValue,int(int(layer_num)/int(total_layers)))

    #     stderr_line = process.stderr.readline()
    #     if stderr_line:
    #         print(stderr_line, end="")  # 实时打印标准错误

    # # 确保进程已完成
    # process.stdout.close()
    # process.stderr.close()
    # process.wait()
    util.send_event_str(util.ProgressValue,100)