import os
import json
import requests

BASE_URL = "https://discourse.onlinedegree.iitm.ac.in/c/courses/tds-kb/34.json?page="
COOKIE = "_forum_session=xktb2XEPZWIHJt4PpTz1gpEaZ6BRZcj%2FDuCgHMVTF0R71BQHAdvbDMdZDwVOtRixI4Bfn9fP7DYmk9ujkcL7tta4DkDO5ot%2B9wgg8YumTjxQnsHS4xeP668Niw4%2Fpb5fzzve7zxqV23colMfXsRslnbRACCmcN83nidJH7k4fD%2BoZtebJEWagR5VNRwiU4LIWhmmJpgvP3hgsUlMBvaisKLo32bXlIo48RD1XRSPFY23RlmXzKJBHy%2BUWRJZTDpfuge4OFu8Zhlkdkzi4tSEyFJT4x32Xe6lT%2BXSYY91H%2B1%2FXfaIOIRK7oaN%2FEr3g%2BN7sCd0QpbRomV%2FhLuYqfaROqSQ2aNxOn1u8W%2FJjWo00yaY1OP4hDQ6G%2FkB8JdpqMHJIbDMiteWld0jDgb4XBRMb6U%2FvBoNavHjVKv3QAtmDXCspyvxiTHxxpST0OmEX%2BEVPOcCsu17G%2FIc9No43kR9oC%2BxJdLEAbvYPS1LKSnAIdFboxCAk2Gz%2BH%2B7VzjoY9s%2FhmpBpRdGP0Z0bn1%2B6UPpyKuQWsxGmJsC3x6drIf9BFBFV%2B71jApRSHSly%2FWOJw%3D%3D--6hb8Ul88tupxKyWf--%2FPZnQW1%2BHSkudQOdEffeDA%3D%3D; _t=QODRSXCaFELJ3x4CYA2YhQgx%2BZWQN0hevsdpRlolFdnpwzLgJ92yIgWNuIJ7kXR2piH2vB7D4QxTpzUL72XqKZQvv2DQaMuByhNgwbXFQPA1ozlW8NbzxTtETnVsLv1RUipi%2F9nTlSeirxc08rEjY196GJt4%2FiMvZPge0s6bzOycdPe1g5ijoFnyUMzSlhTfkb15yWb1cu%2FTUYrgGJY1%2BhW3ZRE1WIjgG%2BxIb5oeTpMG5MxHzV1kwicQv1kN3yvqncy3fqf68xU814QeQkXez2gdeWjaecAmcV%2B4Nxqyzs9cBXn0QS%2BTxsBkz3GSAydd7YmuPw%3D%3D--ta%2FyxyTHYOYCrTw9--IqVd7OM%2Fg0ESI5QTEpPbLw%3D%3D"

os.makedirs("../raw-data/fetched", exist_ok=True)

headers = {"Cookie": COOKIE}

def topics_fetcher(page=30):
    for i in range(page):
        response = requests.get(f"{BASE_URL}{i}", headers=headers)
        response.raise_for_status()
        
        with open(f"../raw-data/fetched/{i}.json", "w") as file:
            json.dump(response.json(), file, indent=2)

        print(f"[{i+1}/{page}] Saved page {i} to ../raw-data/fetched/{i}.json")

if __name__ == "__main__":
    topics_fetcher()

