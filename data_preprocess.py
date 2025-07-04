from datetime import datetime
import os

def parse_line(line):
    parts = line.strip().split('\t')
    user_id = parts[0]
    venue_id = parts[1]
    utc_time_str = parts[7].strip()
    return user_id, venue_id, utc_time_str

def utc_to_millis(utc_time_str):
    dt = datetime.strptime(utc_time_str, "%a %b %d %H:%M:%S %z %Y")
    return int(dt.timestamp() * 1000)

def build_trajectories(input_file, output_file):
    user_traj = {}

    # 时间范围：2012-04-01 到 2013-09-30（UTC 时间戳）
    # start_time = int(datetime(2012, 4, 1, 0, 0, 0).timestamp() * 1000)
    # end_time   = int(datetime(2013, 9, 30, 23, 59, 59).timestamp() * 1000)

    # 读取并过滤时间范围
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            user_id, venue_id, utc_time_str = parse_line(line)
            # 此时 timestamp是整数
            timestamp = utc_to_millis(utc_time_str)
            # if not (start_time <= timestamp <= end_time):
            #    continue
            if user_id not in user_traj:
                user_traj[user_id] = []
            user_traj[user_id].append((venue_id, timestamp))

    # 过滤打卡数 < 20 的用户
    # user_traj = {uid: traj for uid, traj in user_traj.items() if len(traj) >= 20}

    # 写入轨迹文件
    with open(output_file, 'w', encoding='utf-8') as fw:
        for user_id, traj in user_traj.items():
            traj_str = ",".join([f"{loc}@{ts}" for loc, ts in traj])
            fw.write(f"{user_id},{traj_str}\n")

    # 统计信息
    total_users = len(user_traj)
    unique_locations = set()
    total_checkins = 0
    for traj in user_traj.values():
        total_checkins += len(traj)
        unique_locations.update([loc for loc, _ in traj])
    avg_checkins = total_checkins / total_users if total_users > 0 else 0

    # 构造统计文件名
    dataset_name = os.path.splitext(os.path.basename(input_file))[0]
    stat_file = os.path.join(os.path.dirname(output_file), f"{dataset_name}_statics.txt")

    # 写入统计文件
    with open(stat_file, 'w', encoding='utf-8') as sf:
        sf.write(f"Total users: {total_users}\n")
        sf.write(f"Total unique venues: {len(unique_locations)}\n")
        sf.write(f"Total check-ins: {total_checkins}\n")
        sf.write(f"Average check-ins per user: {avg_checkins:.2f}\n")

    print(f"Trajectories have been written to {output_file}")
    print(f"Statistics have been written to {stat_file}")

if __name__ == "__main__":
    input_file = "data/TKY.txt"
    output_file = "data/TKY_trajectories.txt"
    build_trajectories(input_file, output_file)
